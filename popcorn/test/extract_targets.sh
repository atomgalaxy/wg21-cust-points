#!/bin/bash -xe
[[ -z $TEST_TMPDIR ]] && exit 1
out="$TEST_TMPDIR/targets.out"
./popcorn/pop --list ./popcorn/test/in.cpp | tee "$out"
diff -u "$out" - <<EXPECTED
Targets:
--------
first.first.1
first.first.2
first.first.3
first.second.4
first.second.5
first.second.6
EXPECTED

