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
  return 2; //% case #first.second
}

//%    case first {
static_assert(foo(0) == 1); //% OK
static_assert(foo(0) == 2); //% error: does not return 2 in first case
// every error checked separately
static_assert(foo(0) == 3); //% error: does not return 3 in first case
//%    }
//%    case #first.second {
static_assert(foo(0) == 1); //% error
static_assert(foo(0) == 2); //% OK
//% error: applies to next line
static_assert(foo(0) == 3); 
//%    }
//% } 
