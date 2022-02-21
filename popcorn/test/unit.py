import sys
import pytest
import popcorn.popcorn as pc


def _c(s: str) -> pc.Context:
    return pc.parse_context(s, pc.Context(()))


def test_match_case_block_start():
    assert pc.Directive(
        _c("#first.second"), "//% case first.second {", None
    ) == pc.match_case_block_start("//% case first.second {", _c("#"), 0)
    assert pc.Directive(
        _c("#first.second"), "//% case second {", None
    ) == pc.match_case_block_start("//% case second {", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "//% case #blah.second {", None
    ) == pc.match_case_block_start("//% case #blah.second {", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "//% case #blah.second    {", None
    ) == pc.match_case_block_start("//% case #blah.second    {", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "//%     case #blah.second {", None
    ) == pc.match_case_block_start("//%     case #blah.second {", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "      //%     case #blah.second      {", None
    ) == pc.match_case_block_start(
        "      //%     case #blah.second      {", _c("#first"), 0
    )
    assert pc.Directive(
        _c("#blah.second"), "      //%     case #blah.second      {      ", None
    ) == pc.match_case_block_start(
        "      //%     case #blah.second      {      ", _c("#first"), 0
    )
    assert pc.Directive(
        _c("#blah.second"), "      //%     case   #blah.second      {      ", None
    ) == pc.match_case_block_start(
        "      //%     case   #blah.second      {      ", _c("#first"), 0
    )
    assert None == pc.match_case_block_start(
        "      //%     case #blah.second      \n", _c("#first"), 0
    )
    with pytest.raises(pc.SyntaxError):
        pc.match_case_block_start(
            "asdf      //%     case #blah.second    {\n", _c("#first"), 0
        )


def test_match_case_target_block_start_ok():
    assert pc.Directive(
        _c("#first.second"), "//% OK first.second {", pc.OK(_c("#first.second"), "")
    ) == pc.match_case_block_start("//% OK first.second {", _c("#"), 0)
    assert pc.Directive(
        _c("#first.second"),
        "//% OK first.second: a description. {",
        pc.OK(_c("#first.second"), "a description."),
    ) == pc.match_case_block_start("//% OK first.second: a description. {", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "//% OK : a description. {",
        pc.OK(_c("#0"), "a description."),
    ) == pc.match_case_block_start("//% OK : a description. {", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "//% OK {",
        pc.OK(_c("#0"), ""),
    ) == pc.match_case_block_start("//% OK {", _c("#"), 0)

    assert pc.Directive(
        _c("#first.second"), "//% OK second {", pc.OK(_c("#first.second"), "")
    ) == pc.match_case_block_start("//% OK second {", _c("#first"), 0)
    assert pc.Directive(
        _c("#first.second"),
        "//% OK second :    a description.   {",
        pc.OK(_c("#first.second"), "a description."),
    ) == pc.match_case_block_start(
        "//% OK second :    a description.   {", _c("#first"), 0
    )

    assert pc.Directive(
        _c("#blah.second"), "//% OK #blah.second {", pc.OK(_c("#blah.second"), "")
    ) == pc.match_case_block_start("//% OK #blah.second {", _c("#first"), 0)

    assert pc.Directive(
        _c("#blah.second"), "//% OK #blah.second    {", pc.OK(_c("#blah.second"), "")
    ) == pc.match_case_block_start("//% OK #blah.second    {", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "//%     OK #blah.second {", pc.OK(_c("#blah.second"), "")
    ) == pc.match_case_block_start("//%     OK #blah.second {", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "      //%     OK #blah.second      {",
        pc.OK(_c("#blah.second"), ""),
    ) == pc.match_case_block_start(
        "      //%     OK #blah.second      {", _c("#first"), 0
    )
    assert pc.Directive(
        _c("#blah.second"),
        "      //%     OK #blah.second      {      ",
        pc.OK(_c("#blah.second"), ""),
    ) == pc.match_case_block_start(
        "      //%     OK #blah.second      {      ", _c("#first"), 0
    )
    assert pc.Directive(
        _c("#blah.second"),
        "      //%     OK   #blah.second      {      ",
        pc.OK(_c("#blah.second"), ""),
    ) == pc.match_case_block_start(
        "      //%     OK   #blah.second      {      ", _c("#first"), 0
    )
    assert None == pc.match_case_block_start(
        "      //%     OK #blah.second      \n", _c("#first"), 0
    )
    with pytest.raises(pc.SyntaxError):
        pc.match_case_block_start(
            "asdf      //%     OK #blah.second    {\n", _c("#first"), 0
        )


def test_match_case_target_block_start_error():
    assert pc.Directive(
        _c("#first.second"),
        "//% error first.second {",
        pc.Error(_c("#first.second"), ""),
    ) == pc.match_case_block_start("//% error first.second {", _c("#"), 0)
    assert pc.Directive(
        _c("#first.second"),
        "//% error first.second: a description. {",
        pc.Error(_c("#first.second"), "a description."),
    ) == pc.match_case_block_start(
        "//% error first.second: a description. {", _c("#"), 0
    )
    assert pc.Directive(
        _c("#0"),
        "//% error : a description. {",
        pc.Error(_c("#0"), "a description."),
    ) == pc.match_case_block_start("//% error : a description. {", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "//% error : a description.{",
        pc.Error(_c("#0"), "a description."),
    ) == pc.match_case_block_start("//% error : a description.{", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "//% error {",
        pc.Error(_c("#0"), ""),
    ) == pc.match_case_block_start("//% error {", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "//% error{",
        pc.Error(_c("#0"), ""),
    ) == pc.match_case_block_start("//% error{", _c("#"), 0)

    assert pc.Directive(
        _c("#first.second"), "//% error second {", pc.Error(_c("#first.second"), "")
    ) == pc.match_case_block_start("//% error second {", _c("#first"), 0)
    assert pc.Directive(
        _c("#first.second"),
        "//% error second :    a description.   {",
        pc.Error(_c("#first.second"), "a description."),
    ) == pc.match_case_block_start(
        "//% error second :    a description.   {", _c("#first"), 0
    )

    assert pc.Directive(
        _c("#blah.second"), "//% error #blah.second {", pc.Error(_c("#blah.second"), "")
    ) == pc.match_case_block_start("//% error #blah.second {", _c("#first"), 0)

    assert pc.Directive(
        _c("#blah.second"),
        "//% error #blah.second    {",
        pc.Error(_c("#blah.second"), ""),
    ) == pc.match_case_block_start("//% error #blah.second    {", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "//%     error #blah.second {",
        pc.Error(_c("#blah.second"), ""),
    ) == pc.match_case_block_start("//%     error #blah.second {", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "      //%     error #blah.second      {",
        pc.Error(_c("#blah.second"), ""),
    ) == pc.match_case_block_start(
        "      //%     error #blah.second      {", _c("#first"), 0
    )
    assert pc.Directive(
        _c("#blah.second"),
        "      //%     error #blah.second      {      ",
        pc.Error(_c("#blah.second"), ""),
    ) == pc.match_case_block_start(
        "      //%     error #blah.second      {      ", _c("#first"), 0
    )
    assert pc.Directive(
        _c("#blah.second"),
        "      //%     error   #blah.second      {      ",
        pc.Error(_c("#blah.second"), ""),
    ) == pc.match_case_block_start(
        "      //%     error   #blah.second      {      ", _c("#first"), 0
    )
    assert None == pc.match_case_block_start(
        "      //%     error #blah.second      \n", _c("#first"), 0
    )
    with pytest.raises(pc.SyntaxError):
        pc.match_case_block_start(
            "asdf      //%     error #blah.second    {\n", _c("#first"), 0
        )


def test_match_case_next_line():
    assert pc.Directive(
        _c("#first.second"), "//% case first.second ", None
    ) == pc.match_case_next_line("//% case first.second ", _c("#"), 0)
    assert pc.Directive(
        _c("#first.second"), "//% case second ", None
    ) == pc.match_case_next_line("//% case second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "//% case #blah.second ", None
    ) == pc.match_case_next_line("//% case #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "//% case #blah.second    ", None
    ) == pc.match_case_next_line("//% case #blah.second    ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "//%     case #blah.second ", None
    ) == pc.match_case_next_line("//%     case #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "//%     case    #blah.second ", None
    ) == pc.match_case_next_line("//%     case    #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "      //%     case #blah.second      ", None
    ) == pc.match_case_next_line(
        "      //%     case #blah.second      ", _c("#first"), 0
    )
    assert None == pc.match_case_next_line(
        "asdf      //%     case #blah.second      \n", _c("#first"), None
    )


def test_match_case_next_line_ok():
    assert pc.Directive(
        _c("#first.second"), "//% OK first.second", pc.OK(_c("#first.second"), "")
    ) == pc.match_case_next_line("//% OK first.second", _c("#"), 0)
    assert pc.Directive(
        _c("#first.second"),
        "//% OK first.second: a description.",
        pc.OK(_c("#first.second"), "a description."),
    ) == pc.match_case_next_line("//% OK first.second: a description.", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "//% OK : a description.",
        pc.OK(_c("#0"), "a description."),
    ) == pc.match_case_next_line("//% OK : a description.", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "//% OK ",
        pc.OK(_c("#0"), ""),
    ) == pc.match_case_next_line("//% OK ", _c("#"), 0)

    assert pc.Directive(
        _c("#first.second"), "//% OK first.second ", pc.OK(_c("#first.second"), "")
    ) == pc.match_case_next_line("//% OK first.second ", _c("#"), 0)
    assert pc.Directive(
        _c("#first.second"), "//% OK second ", pc.OK(_c("#first.second"), "")
    ) == pc.match_case_next_line("//% OK second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "//% OK #blah.second ", pc.OK(_c("#blah.second"), "")
    ) == pc.match_case_next_line("//% OK #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "//% OK #blah.second    ", pc.OK(_c("#blah.second"), "")
    ) == pc.match_case_next_line("//% OK #blah.second    ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "//%     OK #blah.second ", pc.OK(_c("#blah.second"), "")
    ) == pc.match_case_next_line("//%     OK #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "//%     OK    #blah.second ", pc.OK(_c("#blah.second"), "")
    ) == pc.match_case_next_line("//%     OK    #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "      //%     OK #blah.second      ",
        pc.OK(_c("#blah.second"), ""),
    ) == pc.match_case_next_line("      //%     OK #blah.second      ", _c("#first"), 0)
    assert None == pc.match_case_next_line(
        "asdf      //%     OK #blah.second      \n", _c("#first"), None
    )


def test_match_case_next_line_error():
    assert pc.Directive(
        _c("#first.second"), "//% error first.second", pc.Error(_c("#first.second"), "")
    ) == pc.match_case_next_line("//% error first.second", _c("#"), 0)
    assert pc.Directive(
        _c("#first.second"),
        "//% error first.second: a description.",
        pc.Error(_c("#first.second"), "a description."),
    ) == pc.match_case_next_line("//% error first.second: a description.", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "//% error : a description.",
        pc.Error(_c("#0"), "a description."),
    ) == pc.match_case_next_line("//% error : a description.", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "//% error ",
        pc.Error(_c("#0"), ""),
    ) == pc.match_case_next_line("//% error ", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "//% error: a description",
        pc.Error(_c("#0"), "a description"),
    ) == pc.match_case_next_line("//% error: a description", _c("#"), 0)

    assert pc.Directive(
        _c("#first.second"),
        "//% error first.second ",
        pc.Error(_c("#first.second"), ""),
    ) == pc.match_case_next_line("//% error first.second ", _c("#"), 0)
    assert pc.Directive(
        _c("#first.second"), "//% error second ", pc.Error(_c("#first.second"), "")
    ) == pc.match_case_next_line("//% error second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "//% error #blah.second ", pc.Error(_c("#blah.second"), "")
    ) == pc.match_case_next_line("//% error #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "//% error #blah.second    ",
        pc.Error(_c("#blah.second"), ""),
    ) == pc.match_case_next_line("//% error #blah.second    ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "//%     error #blah.second ",
        pc.Error(_c("#blah.second"), ""),
    ) == pc.match_case_next_line("//%     error #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "//%     error    #blah.second ",
        pc.Error(_c("#blah.second"), ""),
    ) == pc.match_case_next_line("//%     error    #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "      //%     error #blah.second      ",
        pc.Error(_c("#blah.second"), ""),
    ) == pc.match_case_next_line(
        "      //%     error #blah.second      ", _c("#first"), 0
    )
    assert None == pc.match_case_next_line(
        "asdf      //%     error #blah.second      \n", _c("#first"), None
    )


def test_match_this_line():
    assert pc.Directive(
        _c("#first.second"), "asdf //% case first.second ", None
    ) == pc.match_case_this_line("asdf //% case first.second ", _c("#"), 0)
    assert pc.Directive(
        _c("#first.second"), "asdf //% case second ", None
    ) == pc.match_case_this_line("asdf //% case second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "asdf  //% case #blah.second ", None
    ) == pc.match_case_this_line("asdf  //% case #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "asdf//% case #blah.second    ", None
    ) == pc.match_case_this_line("asdf//% case #blah.second    ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "asdf//%     case #blah.second ", None
    ) == pc.match_case_this_line("asdf//%     case #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "asdf//%     case   #blah.second ", None
    ) == pc.match_case_this_line("asdf//%     case   #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "asdf      //%     case #blah.second      ", None
    ) == pc.match_case_this_line(
        "asdf      //%     case #blah.second      ", _c("#first"), 0
    )
    assert None == pc.match_case_this_line(
        "asdf      //%     #blah.second      \n", _c("#first"), 0
    )


def test_match_this_line_ok():
    assert pc.Directive(
        _c("#first.second"), "asdf  //% OK first.second", pc.OK(_c("#first.second"), "")
    ) == pc.match_case_this_line("asdf  //% OK first.second", _c("#"), 0)
    assert pc.Directive(
        _c("#first.second"),
        "asdf //% OK first.second: a description.",
        pc.OK(_c("#first.second"), "a description."),
    ) == pc.match_case_this_line("asdf //% OK first.second: a description.", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "// asdf //% OK : a description.",
        pc.OK(_c("#0"), "a description."),
    ) == pc.match_case_this_line("// asdf //% OK : a description.", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "asdf //% OK ",
        pc.OK(_c("#0"), ""),
    ) == pc.match_case_this_line("asdf //% OK ", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "//% OK: a description",
        pc.OK(_c("#0"), "a description"),
    ) == pc.match_case_this_line("//% OK: a description", _c("#"), 0)

    assert pc.Directive(
        _c("#first.second"), "asdf //% OK first.second ", pc.OK(_c("#first.second"), "")
    ) == pc.match_case_this_line("asdf //% OK first.second ", _c("#"), 0)
    assert pc.Directive(
        _c("#first.second"), "asdf //% OK second ", pc.OK(_c("#first.second"), "")
    ) == pc.match_case_this_line("asdf //% OK second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "asdf  //% OK #blah.second ", pc.OK(_c("#blah.second"), "")
    ) == pc.match_case_this_line("asdf  //% OK #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"), "asdf//% OK #blah.second    ", pc.OK(_c("#blah.second"), "")
    ) == pc.match_case_this_line("asdf//% OK #blah.second    ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "asdf//%     OK #blah.second ",
        pc.OK(_c("#blah.second"), ""),
    ) == pc.match_case_this_line("asdf//%     OK #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "asdf//%     OK   #blah.second ",
        pc.OK(_c("#blah.second"), ""),
    ) == pc.match_case_this_line("asdf//%     OK   #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "asdf      //%     OK #blah.second      ",
        pc.OK(_c("#blah.second"), ""),
    ) == pc.match_case_this_line(
        "asdf      //%     OK #blah.second      ", _c("#first"), 0
    )
    assert None == pc.match_case_this_line(
        "asdf      //%     #blah.second      \n", _c("#first"), 0
    )


def test_match_this_line_error():
    assert pc.Directive(
        _c("#first.second"),
        "asdf  //% error first.second",
        pc.Error(_c("#first.second"), ""),
    ) == pc.match_case_this_line("asdf  //% error first.second", _c("#"), 0)
    assert pc.Directive(
        _c("#first.second"),
        "asdf //% error first.second: a description.",
        pc.Error(_c("#first.second"), "a description."),
    ) == pc.match_case_this_line(
        "asdf //% error first.second: a description.", _c("#"), 0
    )
    assert pc.Directive(
        _c("#0"),
        "// asdf //% error : a description.",
        pc.Error(_c("#0"), "a description."),
    ) == pc.match_case_this_line("// asdf //% error : a description.", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "asdf //% error ",
        pc.Error(_c("#0"), ""),
    ) == pc.match_case_this_line("asdf //% error ", _c("#"), 0)
    assert pc.Directive(
        _c("#0"),
        "//% error: a description",
        pc.Error(_c("#0"), "a description"),
    ) == pc.match_case_this_line("//% error: a description", _c("#"), 0)

    assert pc.Directive(
        _c("#first.second"),
        "asdf //% error first.second ",
        pc.Error(_c("#first.second"), ""),
    ) == pc.match_case_this_line("asdf //% error first.second ", _c("#"), 0)
    assert pc.Directive(
        _c("#first.second"), "asdf //% error second ", pc.Error(_c("#first.second"), "")
    ) == pc.match_case_this_line("asdf //% error second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "asdf  //% error #blah.second ",
        pc.Error(_c("#blah.second"), ""),
    ) == pc.match_case_this_line("asdf  //% error #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "asdf//% error #blah.second    ",
        pc.Error(_c("#blah.second"), ""),
    ) == pc.match_case_this_line("asdf//% error #blah.second    ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "asdf//%     error #blah.second ",
        pc.Error(_c("#blah.second"), ""),
    ) == pc.match_case_this_line("asdf//%     error #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "asdf//%     error   #blah.second ",
        pc.Error(_c("#blah.second"), ""),
    ) == pc.match_case_this_line("asdf//%     error   #blah.second ", _c("#first"), 0)
    assert pc.Directive(
        _c("#blah.second"),
        "asdf      //%     error #blah.second      ",
        pc.Error(_c("#blah.second"), ""),
    ) == pc.match_case_this_line(
        "asdf      //%     error #blah.second      ", _c("#first"), 0
    )
    assert None == pc.match_case_this_line(
        "asdf      //%     #blah.second      \n", _c("#first"), 0
    )


_inf = float("inf")


def test_process_line_block_start():
    stack, dir, left = pc.process_line("//% case first.second {", _c("#"), _inf, 42)
    assert left == _inf
    assert dir == pc.Directive(_c("#first.second"), "//% case first.second {", None)
    assert stack == _c("#first.second")


def test_process_line_block_end():
    stack, dir, left = pc.process_line("//% } ", _c("#a"), _inf, 42)
    assert left == 0
    assert dir == pc.Directive(_c("#a"), "//% } ", None)
    assert stack == None


def test_process_line_block_ok():
    stack, dir, left = pc.process_line(
        "//% OK first.second: comment {", _c("#"), _inf, 42
    )
    assert left == _inf
    assert dir == pc.Directive(
        _c("#first.second"),
        "//% OK first.second: comment {",
        pc.OK(_c("#first.second"), "comment"),
    )
    assert stack == _c("#first.second")


def test_process_line_next_line_start():
    stack, dir, left = pc.process_line("//% case first.second", _c("#"), _inf, 42)
    assert left == 1
    assert dir == pc.Directive(_c("#first.second"), "//% case first.second", None)
    assert stack == _c("#first.second")


def test_process_line_next_line_ok():
    stack, dir, left = pc.process_line(
        "//% OK first.second: comment", _c("#"), _inf, 42
    )
    assert left == 1
    assert dir == pc.Directive(
        _c("#first.second"),
        "//% OK first.second: comment",
        pc.OK(_c("#first.second"), "comment"),
    )
    assert stack == _c("#first.second")


def test_process_line_this_line_start():
    stack, dir, left = pc.process_line("asdf //% case first.second", _c("#"), 4, 42)
    assert left == 3
    assert dir == pc.Directive(_c("#first.second"), "asdf //% case first.second", None)
    assert stack == None


def test_process_line_this_line_ok():
    stack, dir, left = pc.process_line(
        "asdf //% OK first.second: comment", _c("#"), 2, 42
    )
    assert left == 1
    assert dir == pc.Directive(
        _c("#first.second"),
        "asdf //% OK first.second: comment",
        pc.OK(_c("#first.second"), "comment"),
    )
    assert stack == None


def test_process_line_text():
    stack, dir, left = pc.process_line(
        "asdf OK first.second: comment", _c("#"), _inf, 42
    )
    assert left == _inf
    assert dir == pc.TextLine(_c("#"), "asdf OK first.second: comment")
    assert stack == None


def test_process_line_text_cont():
    stack, dir, left = pc.process_line("asdf OK first.second: comment", _c("#"), 1, 42)
    assert left == 0
    assert dir == pc.TextLine(_c("#"), "asdf OK first.second: comment")
    assert stack == None


def test_extract_targets_simple():
    input = """
//% case first {
    asdf //% OK
//% }
"""
    expected = {
        pc.OK(_c("#first.1"), ""),
    }
    r = pc.process(input)
    actual = r.targets
    assert expected == actual

    variants = {
        pc.OK(_c("#first.1"), ""): (
            pc.TextLine(_c("#"), ""),
            pc.Directive(_c("#first"), "//% case first {", None),
            pc.Directive(_c("#first.1"), "    asdf //% OK", pc.OK(_c("#first.1"), "")),
            pc.Directive(_c("#first"), "//% }", None),
        )
    }
    for key in variants:
        assert variants[key] == r.outputs[key]
    assert variants == r.outputs


def test_extract_targets_more_complex():
    input = """
//% case first {
    asdf //% OK
    jkl; //% error second: desc
    //% case third
    blorg //% OK
    //% error fourth {
        blarg
        blurg
    //% }
    blirg //% error
//% }
"""
    expected = {
        pc.OK(_c("#first.1"), ""),
        pc.Error(_c("#first.second"), "desc"),
        pc.OK(_c("#first.third.3"), ""),
        pc.Error(_c("#first.fourth"), ""),
        pc.Error(_c("#first.5"), ""),
    }
    r = pc.process(input)
    actual = r.targets
    assert expected == actual

    variants = {
        pc.OK(
            _c("#first.1"), ""
        ): """
//% case first {
    asdf //% OK
//% }
""",
        pc.Error(
            _c("#first.second"), "desc"
        ): """
//% case first {
    jkl; //% error second: desc
//% }
""",
        pc.OK(
            _c("#first.third.3"), ""
        ): """
//% case first {
    //% case third
    blorg //% OK
//% }
""",
        pc.Error(
            _c("#first.fourth"), ""
        ): """
//% case first {
    //% error fourth {
        blarg
        blurg
    //% }
//% }
""",
        pc.Error(
            _c("#first.5"), ""
        ): """
//% case first {
    blirg //% error
//% }
""",
    }
    actual_rendered = {t: pc.render_variant(r.outputs[t]) for t in r.targets}
    for key in variants:
        assert variants[key] == actual_rendered[key]
    assert variants == actual_rendered


if __name__ == "__main__":
    exit(pytest.main([__file__, "-v"]))
