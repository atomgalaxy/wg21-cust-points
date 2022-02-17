/* test declaring a simple CPO with a default and an override */

namespace generic {
template <typename... Args> virtual constexpr auto cpo(Args...) = 0;
constexpr auto cpo(auto &&x) default { return 2; }
} // namespace generic

namespace associated {
struct X {
  template <auto cpo> constexpr auto cpo(X) override { return 1; }
};
} // namespace associated

int main() {
  static_assert(generic::cpo(associated::X{}) == 1);
  static_assert(generic::cpo(1) == 2);
}
