#pragma once

#include <driver/gpio.h>

constexpr gpio_num_t kOledSda = GPIO_NUM_1;
constexpr gpio_num_t kOledScl = GPIO_NUM_2;
constexpr gpio_num_t kSpeakerBclk = GPIO_NUM_43;
constexpr gpio_num_t kSpeakerLrck = GPIO_NUM_5;
constexpr gpio_num_t kSpeakerData = GPIO_NUM_7;
constexpr gpio_num_t kMicClock = GPIO_NUM_42;
constexpr gpio_num_t kMicData = GPIO_NUM_41;
constexpr gpio_num_t kPanSignal = GPIO_NUM_4;
constexpr gpio_num_t kTiltSignal = GPIO_NUM_6;
constexpr gpio_num_t kHeadButton = GPIO_NUM_44;
constexpr gpio_num_t kChatButton = GPIO_NUM_0;
