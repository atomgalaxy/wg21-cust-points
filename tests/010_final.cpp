/* test declarations and calling of final functions */

namespace test_final {

// declaration
template <typename I, typename S> virtual constexpr I cpo(I, S) final;

// definition
template <typename I, typename S> virtual constexpr I cpo(I, S) final {
  return I{};
};

// ill-formed: can't have both a customizable and a final share a name.
virtual constexpr int cpo() = 0;

// ill-formed: override (previously marked final)
auto cpo(int, long) override;
// ill-formed: default (previously marked final)
auto cpo(long, int) default;

namespace unrelated {
// ill-formed: override (previously marked final)
auto ::test_final_001::cpo(int, long) override;
// ill-formed: default (previously marked final)
auto ::test_final_001::cpo(long, int) default;
} // namespace unrelated

} // namespace test_final_001
