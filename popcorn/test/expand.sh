#!/bin/bash -xe
[[ -z $TEST_TMPDIR ]] && exit 1
out="$TEST_TMPDIR/expand"
mkdir -p "$out"
./popcorn/pop --out-dir "$out" ./popcorn/test/in.cpp
diff -u "$out" "popcorn/test/expected"
