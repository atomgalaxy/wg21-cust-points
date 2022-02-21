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
