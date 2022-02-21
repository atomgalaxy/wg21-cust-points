#!/bin/bash -xe
[[ -z $TEST_TMPDIR ]] && exit 1
out="$TEST_TMPDIR/expand"
mkdir -p "$out"
./popcorn/pop --out-dir "$out" ./popcorn/test/in.cpp --dry-run | tee "$out/log.out"
diff -u "$out/log.out" - <<EXPECTED
$out/first.first.2.Error.cpp
--------
/**
 * input file for popcorn
 * 
 * This comment should be left alone and added to every part of the test.
 */

void preamble(int x) {
  // this function will be in every test
}

//% case first {
constexpr auto foo(...) {
  // check inline unanchored names
  return 1; //% case first
  // check anchored names
}

//%    case first {
static_assert(foo(0) == 2); //% error: does not return 2 in first case
// every error checked separately
//%    }
//% } 


$out/first.first.3.Error.cpp
--------
/**
 * input file for popcorn
 * 
 * This comment should be left alone and added to every part of the test.
 */

void preamble(int x) {
  // this function will be in every test
}

//% case first {
constexpr auto foo(...) {
  // check inline unanchored names
  return 1; //% case first
  // check anchored names
}

//%    case first {
// every error checked separately
static_assert(foo(0) == 3); //% error: does not return 3 in first case
//%    }
//% } 


$out/first.second.4.Error.cpp
--------
/**
 * input file for popcorn
 * 
 * This comment should be left alone and added to every part of the test.
 */

void preamble(int x) {
  // this function will be in every test
}

//% case first {
constexpr auto foo(...) {
  // check inline unanchored names
  // check anchored names
  return 2; //% case #first.second
}

//%    case #first.second {
static_assert(foo(0) == 1); //% error
//%    }
//% } 


$out/first.second.6.Error.cpp
--------
/**
 * input file for popcorn
 * 
 * This comment should be left alone and added to every part of the test.
 */

void preamble(int x) {
  // this function will be in every test
}

//% case first {
constexpr auto foo(...) {
  // check inline unanchored names
  // check anchored names
  return 2; //% case #first.second
}

//%    case #first.second {
//% error: applies to next line
static_assert(foo(0) == 3); 
//%    }
//% } 


$out/first.first.1.OK.cpp
--------
/**
 * input file for popcorn
 * 
 * This comment should be left alone and added to every part of the test.
 */

void preamble(int x) {
  // this function will be in every test
}

//% case first {
constexpr auto foo(...) {
  // check inline unanchored names
  return 1; //% case first
  // check anchored names
}

//%    case first {
static_assert(foo(0) == 1); //% OK
// every error checked separately
//%    }
//% } 


$out/first.second.5.OK.cpp
--------
/**
 * input file for popcorn
 * 
 * This comment should be left alone and added to every part of the test.
 */

void preamble(int x) {
  // this function will be in every test
}

//% case first {
constexpr auto foo(...) {
  // check inline unanchored names
  // check anchored names
  return 2; //% case #first.second
}

//%    case #first.second {
static_assert(foo(0) == 2); //% OK
//%    }
//% } 


EXPECTED
