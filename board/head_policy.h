#pragma once

namespace head_policy {
constexpr int kMinPosition = -10;
constexpr int kMaxPosition = 10;
constexpr int kCenterUs = 1500;
constexpr int kUsPerPosition = 10;
constexpr int kPanSign = 1;
constexpr int kTiltSign = 1;
constexpr int kStepUs = 5;
constexpr int kPeriodUs = 20000;
constexpr int kResolutionBits = 13;

constexpr bool ValidPosition(int value) {
    return value >= kMinPosition && value <= kMaxPosition;
}

constexpr int PulseUs(int position, int sign) {
    return kCenterUs + position * kUsPerPosition * sign;
}

constexpr int Approach(int current, int target) {
    const int delta = target - current;
    return current + (delta > kStepUs ? kStepUs : delta < -kStepUs ? -kStepUs : delta);
}

constexpr unsigned Duty(int pulse_us) {
    return static_cast<unsigned>((static_cast<long long>(pulse_us) *
                                  (1 << kResolutionBits) + kPeriodUs / 2) / kPeriodUs);
}

static_assert(kPanSign == 1 || kPanSign == -1);
static_assert(kTiltSign == 1 || kTiltSign == -1);
static_assert(PulseUs(kMinPosition, 1) >= 1000);
static_assert(PulseUs(kMaxPosition, 1) <= 2000);
}
