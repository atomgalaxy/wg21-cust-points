#!/bin/bash -xe

[[ -z $TEST_TMPDIR ]] && exit 1
out="$TEST_TMPDIR/docs.md"
./popcorn/pop --help > "$out"
diff "$out" ./popcorn/README.md
