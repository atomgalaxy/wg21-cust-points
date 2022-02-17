// TODO: test the new compiler-magic resolve_override_v<cpo, Args...> trait
// which returns the function pointer to the prototype that the arglist would
// dispatch to.
//
// This is different from a static_cast because it
// a) deduces the return type,
// b) arg types don't have to exactly match.
