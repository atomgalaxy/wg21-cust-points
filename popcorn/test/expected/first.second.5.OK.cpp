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
