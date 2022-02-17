# Final (non) customisable functions

Final customisable functions allow the creation of CFO that are not customisable for types defined in another namespace.
They can have neither `default` nor `override` implementations.
Unlike CFO prototypes, they can have default parameters.

Like other CFO, they are not found by ADL, and they define an object such that the overload set can be forwarded to other functions.


This allows to match the behaviour of standard algorithms in the ranges namespace (colloquially named niebloids), described as follow:

> The entities defined in the std::anges namespace in this Clause are not found by argument-dependent name lookup ([basic.lookup.argdep]).
> When found by unqualified ([basic.lookup.unqual]) name lookup for the postfix-expression in a function call ([expr.call]), they inhibit argument-dependent name lookup.


```cpp
#include <iterator>
#include <vector>


namespace std::ranges {

// Forward declaration of a final (non customisable) customisable function
template<input_iterator I, sentinel_for<I> S, class T, class Proj = identity>
virtual constexpr I find(I first, S last, const T& value, Proj proj = {}) final; // declared with the final virt-specifier


// definition of the above function
template<input_iterator I, sentinel_for<I> S, class T, class Proj = identity>
virtual constexpr I find(I first, S last, const T& value, Proj proj = {}) final {
    // ...
}

// default: ill-formed (previously marked final)
template<input_iterator I, sentinel_for<I> S, class T, class Proj = identity>
virtual constexpr I find(I first, S last, const T& value, Proj proj = {}) default; // ILL-FORMED


// override: ill-formed (previously marked final)
template<forward_iterator I, sentinel_for<I> S, class T, class Proj = identity>
virtual constexpr I find(I first, S last, const T& value, Proj proj = {}) override;  // ILL-FORMED


// Ill-formed: can't have both customisable and final overloads in the same overload
template<input_range R, class T, class Proj = identity>
virtual constexpr auto find(R&& r) = 0;  // ILL-FORMED

// Different overload for the same CFO
template<input_range R, class T, class Proj = identity>
virtual constexpr auto find(R&& r, const T& value, Proj proj = {}) final {
    //...
    return {};
}

} // std::ranges
```

Final customisable functions act like usual customisable functions:
 * They create an object
 * They are not found by ADL

```cpp

void consume_cpo(auto&& cpo);

int main()  {
    consume_cpo(std::ranges::find) // Ok (find is an object representing the overload set)
    std::vector<int> v;
    std::ranges::find(v, 42); //
    find(std::ranges::views::all(v), 42); // ill-formed, find is not found by adl
}

```

When a non-customisable final CPOs is found by unqualified lookup, ADL is not performed:

```cpp
int main()  {
    using namespace std::ranges;
    std::vector<int> v;
    find(v.begin(), v.end(), 42); // call std::ranges::find
                                  // std::find is **not** found, even if more specialized than std::ranges::find
}
```
