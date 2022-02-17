/* if the prototype is noexcept then the chosen overload must be as well */

namespace noexcept_check {
template <typename... Args> virtual constexpr auto cpo(Args...) noexcept = 0;
constexpr auto cpo(auto &&x) default { return 2; }
} // namespace noexcept_check

namespace associated {
struct X {};
constexpr auto ::noexcept_check::cpo(X) override noexcept { return 1; }
} // namespace associated

int main() {
  static_assert(noexcept_check::cpo(associated::X{}) == 1); // ok
  // ill-formed: the chosen override is not noexcept
  static_assert(noexcept_check::cpo(1) == 2);
}
