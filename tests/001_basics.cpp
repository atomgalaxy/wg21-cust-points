/* test declaring a simple CPO with a default and an override */

namespace basics {
template <typename... Args> virtual constexpr auto cpo(Args...) = 0;
constexpr auto cpo(auto &&x) default { return 2; }
} // namespace basics

namespace associated {
struct X {};
constexpr auto ::basics::cpo(X) override { return 1; }
} // namespace associated

int main() {
  static_assert(basics::cpo(associated::X{}) == 1);
  static_assert(basics::cpo(1) == 2);
}
