#include "../board/head_policy.h"
#include <cassert>
#include <climits>

int main() {
    using namespace head_policy;
    assert(!ValidPosition(INT_MIN));
    assert(!ValidPosition(-11));
    assert(ValidPosition(-10));
    assert(ValidPosition(0));
    assert(ValidPosition(10));
    assert(!ValidPosition(11));
    assert(!ValidPosition(INT_MAX));
    assert(PulseUs(-10, 1) == 1400);
    assert(PulseUs(10, 1) == 1600);
    assert(PulseUs(-10, -1) == 1600);
    assert(Duty(1500) == 614);
    for (int target = 1400; target <= 1600; ++target) {
        int current = 1500;
        for (int step = 0; step < 50; ++step) {
            const int next = Approach(current, target);
            assert(next >= 1400 && next <= 1600);
            assert(next - current <= 5 && current - next <= 5);
            current = next;
        }
        assert(current == target);
    }
}
