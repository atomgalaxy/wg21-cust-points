from __future__ import annotations

import re
import argparse
import typing
import dataclasses
import pathlib
import types


@dataclasses.dataclass(frozen=True)
class Context:
    target: tuple[str, ...]

    def is_parent_of(self, context: Context) -> bool:
        if len(self) > len(context):
            return False
        return self.target == context.target[: len(self)]

    def __len__(self):
        return len(self.target)

    def __str__(self):
        if len(self) == 1:
            return '#'
        return '.'.join(self.target[1:])


class SyntaxError(RuntimeError):
    def __init__(self, msg):
        super().__init__(msg)
        self.lineno = "<unknown>"
        self.line = "<unset>"
        self.file = "<string>"

    def __str__(self):
        return f"Syntax Error in {self.file}:{self.lineno}: {self.args[0]}\n>   {self.line}"


def parse_context(name: str, context: Context) -> Context:
    if name == "#":
        return Context(("#",))
    if name.startswith("#"):
        return Context(("#", *name[1:].split(".")))
    return Context((*context.target, *name.split(".")))


@dataclasses.dataclass(frozen=True)
class OK:
    context: Context
    description: str


@dataclasses.dataclass(frozen=True)
class Error:
    context: Context
    description: str


@dataclasses.dataclass(frozen=True)
class TextLine:
    context: Context
    line: str

    @property
    def target(self):
        return None


@dataclasses.dataclass(frozen=True)
class Directive:
    context: Context
    line: str
    target: typing.Optional[typing.Union[OK, Error]]


@dataclasses.dataclass(frozen=True)
class Source:
    input: str
    targets: frozenset[Context]
    outputs: dict[Context, tuple[typing.Union[Directive, TextLine]]]


TARGET_NAME = r"(?P<name>#?[\w.]+)"
TARGET_MATCH = rf"(?P<kind>OK|error)(\s+({TARGET_NAME}))?(\s*:(?P<desc>.*))?"
MATCH_CASE_BLOCK_START = re.compile(rf"//%\s+case\s+{TARGET_NAME}\s*{{\s*$")
MATCH_CASE_TARGET_BLOCK_START = re.compile(rf"//%\s+{TARGET_MATCH}\s*{{\s*$")
MATCH_CASE_NEXT_LINE = re.compile(rf"^\s*//%\s+case\s+{TARGET_NAME}\s*$")
MATCH_CASE_TARGET_NEXT_LINE = re.compile(rf"^\s*//%\s+{TARGET_MATCH}\s*$")
MATCH_CASE_THIS_LINE = re.compile(rf"//%\s+case\s+{TARGET_NAME}\s*$")
MATCH_CASE_TARGET_THIS_LINE = re.compile(rf"//%\s+{TARGET_MATCH}\s*$")
CASE_END = re.compile(rf"^\s*//%\s+}}\s*")


def parse_target(
    line: str, context: Context, groups: re.Match, target_serial: int
) -> typing.Union[OK, Error]:
    name = groups["name"]
    if not name:
        name = str(target_serial)
    new_context = parse_context(name, context)
    kind = groups["kind"]
    description = (groups["desc"] or "").strip()

    return Directive(
        new_context, line, {"OK": OK, "error": Error}[kind](new_context, description)
    )


def match_case_block_start(
    line: str, context: Context, target_serial: int
) -> typing.Optional[Directive]:
    groups = MATCH_CASE_BLOCK_START.search(line)
    if groups:
        if not line.lstrip().startswith("//%"):
            raise SyntaxError("A block start has to be on its own line.")

        return Directive(parse_context(groups["name"], context), line, None)

    groups = MATCH_CASE_TARGET_BLOCK_START.search(line)
    if groups:
        if not line.lstrip().startswith("//%"):
            raise SyntaxError("A block start has to be on its own line.")
        return parse_target(line, context, groups, target_serial)


def match_case_next_line(
    line: str, context: Context, target_serial: int
) -> typing.Optional[Directive]:
    groups = MATCH_CASE_NEXT_LINE.search(line)
    if groups:
        return Directive(parse_context(groups["name"], context), line, None)

    groups = MATCH_CASE_TARGET_NEXT_LINE.search(line)
    if groups:
        return parse_target(line, context, groups, target_serial)


def match_case_this_line(
    line: str, context: Context, target_serial: int
) -> typing.Optional[Directive]:
    groups = MATCH_CASE_THIS_LINE.search(line)
    if groups:
        return Directive(parse_context(groups["name"], context), line, None)

    groups = MATCH_CASE_TARGET_THIS_LINE.search(line)
    if groups:
        return parse_target(line, context, groups, target_serial)


def match_case_block_end(line: str) -> bool:
    return CASE_END.match(line)


Numeric = typing.Union[int, float]


def process_line(line: str, context: Context, ctx_left: Numeric, target_serial: int):
    maybe_block_ctx = match_case_block_start(line, context, target_serial)
    if maybe_block_ctx:
        if ctx_left != float("inf"):
            raise SyntaxError("Can't start a block while in next-line mode.")
        return maybe_block_ctx.context, maybe_block_ctx, float("inf")

    maybe_next_line_ctx = match_case_next_line(line, context, target_serial)
    if maybe_next_line_ctx:
        if ctx_left != float("inf"):
            raise SyntaxError("Can't start a next-line mode while in next-line mode.")
        return maybe_next_line_ctx.context, maybe_next_line_ctx, 1

    maybe_this_line_ctx = match_case_this_line(line, context, target_serial)
    if maybe_this_line_ctx:
        return None, maybe_this_line_ctx, ctx_left - 1

    if match_case_block_end(line):
        return None, Directive(context, line, None), 0

    # normal line
    return None, TextLine(context, line), ctx_left - 1


def select_lines(directives, target):
    return tuple(d for d in directives if d.context.is_parent_of(target))


def process(input: str) -> Source:
    context_stack = [Context(("#",))]
    lines_left = float("inf")
    target_serial = 1
    lines = []

    try:
        for lineno, line in enumerate(input.splitlines(), 1):
            maybe_new_context, directive, lines_left = process_line(
                line, context_stack[-1], lines_left, target_serial
            )
            lines.append(directive)
            if directive.target:
                target_serial += 1
            if maybe_new_context:
                context_stack.append(maybe_new_context)
            elif lines_left == 0:
                context_stack.pop()
                lines_left = float("inf")
    except SyntaxError as e:
        e.lineno = lineno
        e.line = line
        raise

    targets = frozenset(v.target for v in lines if v.target)
    outputs = {target: select_lines(lines, target.context) for target in targets}
    return Source(input=input, targets=targets, outputs=outputs)


def render_variant(lines):
    return "".join(f"{line.line}\n" for line in lines)


def argument_parser():
    p = argparse.ArgumentParser()
    p.add_argument("input_file", help="Input file", type=pathlib.Path)
    p.add_argument("--out-dir", help="Output directory.", type=pathlib.Path)
    p.add_argument('--list', action="store_true", help="Just list the targets.")
    p.add_argument('--dry-run', action="store_true", help="Instead of writing files, print their names and contents.")
    return p


def get_opts(argv: typing.Optional[list]):
    opts = argument_parser().parse_args(argv)
    if opts.out_dir and not opts.out_dir.is_dir():
        raise RuntimeError(f"--out-dir must exist, but {opts.out_dir} does not.")

    return opts


def main(argv=None):
    opts = get_opts(argv)
    input_file = opts.input_file.read_text()
    try:
        r = process(input_file)
    except SyntaxError as e:
        e.file = opts.input_file
        raise 
    if opts.list:
        print("Targets:")
        print("--------")
        print("\n".join(sorted(str(t.context) for t in r.targets)))
    if opts.out_dir:
        ext = opts.input_file.suffix
        for t in sorted(r.targets, key=str):
            out = opts.out_dir / f"{t.context}.{t.__class__.__name__}{ext}"
            rendered = render_variant(r.outputs[t])
            if opts.dry_run:
                print(out)
                print("--------")
                print(rendered)
                print()
            else:
                print(f"writing {out}...")
                out.write_text(rendered)


if __name__ == "__main__":
    main()
