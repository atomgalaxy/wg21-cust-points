# Examples in P2547

## Rules

Given a postfix-expression `cpo(args...)`, overload resolution proceeds as
follows:

0) form the set of associated `cpo` overrides using usual associated-entity
   rules. Hidden friends, associated namespaces, etc. This includes generic
   CPO overrides.

1) form the overload set of prototypes of `cpo`, including defaults
   (keep default prototypes marked default, they won't win against any other
   match). This uses normal template signature deduction etc.
   You now have a set of function signatures.

2) for every function signature from (1), form a pro-forma call expression
   corresponding to the argument types.
   For every override from (0), try to form a call-expression corresponding
   to this pro-forma function signature. This includes template argument
   deduction for function templates in set (0), and eliminates any failed
   deduction (SFINAE/concepts), `noexcept` specification mismatches, and
   return type concept check failures.

   This step results in a set of "viable" overrides per prototype.

3) Union these sets to eliminate duplicates; default and non-default
   overrides do not correspond.

   We now have two sets of overrides; the _non-default_ overrides, and
   _default_ overrides.

   Starting with the non-default set, perform normal overload resolution on
   the actual postfix-expression `f(a)` with `f` from this set.

   (Aside: recall that normal overload resolution includes full conversion
   sequences, functions having precedence over function template
   specializations, which have precedence over c-variadics, and so on.)

   If this step results in zero viable candidates, perform "normal" overload
   resolution on the set of default overrides.

### Inheriting from CPOs

The expression `cpo(a)` may be a result of implicit conversions:

```cpp
inline constexpr struct F : decltype(cpo) {} f;
```

`f(args...)` exhibits the same behaviour through conversion-to-base, for every
base that is a cpo type.

Note: inheriting from several CPOs will form an overload set from all of them.
Note: if one also defines additional `operator()` on `F`, those also become part of overload resolution, as one would expect.

In other words, CPOs behave as-if they were objects with a consistent overload set of `operator()` and thus interoperate with the rest of the language seamlessly.

### Surrogate-like behaviour rejected

We considered allowing surrogate-like behaviour but it's not implementable in
any kind of sensible fashion.

Note: surrogate behaviour:

```cpp
inline constexpr struct H {
   constexpr operator decltype(cpo)() const { return cpo; }
} h;
h(args...); // could behave like `cpo(args...)`
```

The problem with this approach is that

```cpp
inline constexpr struct All {
   template <typename T>
   constexpr operator T () const { return T{}; }
} all;
// would require compiler to try every CPO in the translation unit
// which is clearly too much and a bug-farm
all(args...);
```

## Examples

### Generic forwarding

#### conversions 1

```cpp
virtual void foo(auto& obj, auto val) = 0;

struct my_type {
  friend void foo(my_type& x, auto val) override {}
};

template <typename Inner>
struct wrapper {
  Inner inner;

  template<auto cpo, typename... Args>
  friend decltype(auto) cpo(wrapper w, Args... args) override {
    return cpo(w.inner, (Args&&)args...);
  }
};

string val = "hello";
my_type x;
// winning overload: foo(my_type&, string)
foo(x, val); // x by lvalue-ref, val by copy

wrapper<my_type> w;
// winning overload: foo(wrapper<my_type>, string)
foo(w, val); // w by copy, val by copy
```

#### conversions 2

```cpp
virtual R foo(auto x, auto y) = 0;   // 1
virtual R foo(auto& x, auto& y) = 0; // 2
virtual R foo(int x, int y) = 0;     // 3

struct X {
   template <auto cpo, typename T>
   decltype(auto) cpo(X&&, T x) override;   // 4
};

foo(X{}, 2);                                // 5
X x; int i = 2;
foo(x, i);                                  // 6
```

line (5) resolves as:

- only (1) matches; if X had an implicit conversion to int, (3) would also.
- we get a call expression of type R(foo)(X prvalue, int prvalue)
- we match (4) against that and deduce cpo = foo, T = int to produce R foo(X&&, int)
- that's a valid match for (5) so it works.

line (6) resolves as:

- (1) and (2) match
- for (1), (4) yields R foo(X&&, int) (a)
- for (2), (4) yields R foo(X&&, int) from template instantiation but X& fails to req with X&& so it's not added to the overload set
- (6) is attempted with (a) and fails.

#### conversions 3; pathology

```cpp
virtual void foo(int) = 0;  // 1
void foo(long) override {}; // 2
struct X { operator int() const; operator long() const; };
foo(X{}); // calls (2)
```

- `foo(int)` is callable with `f(X{})` because `X` has an implicit conversion to `int`
- there is a `foo(long)` override that is callable with an expression `foo(int)`, which is selected and substituted as the chosen override
- the expression `foo(X{})` converts `X{}` to `long` and calls the override.

#### conversions 4; not pathology

```cpp
virtual void f(auto) = 0;
void f(double) override;
void f(nullptr_t) override;
f(0); // calls f(double)
```

- `f(auto)` on `f(0)` deduces to `f(int)`
   - `f(double)` is callable with an argument of type `int`; it is added to the overload set
   - `f(nullptr_t)` is *not* callable with an argument of type `int`, and is not added to the overload set
   - -> `f(double)` wins.
- `f(0)` binds to `f(double)` and call succeeds.

#### conversions 5

```cpp
virtual void f(number auto) = 0;
void f(auto) override;   // 1
void f(double) override; // 2
void f(float) override;  // 3
f(0); // 1 wins
```

```cpp
void g(auto&& x) = 0;
void g(int y) {}; // pass by value is faster
g(1); // works, calls g(int)
```

```cpp
virtual void h(number auto) default { };
void h(double) override;
void h(float) override;
h(0); // error, ambiguous, `int` has conversions to both float and double, default is not considered
```

```cpp
virtual void k(number auto) default { }; //  1
void k(same_as<double> auto) override;   //  2
void k(same_as<float> auto) override;    //  3
k(0); // calls 1
```
