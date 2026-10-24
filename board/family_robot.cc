#include "wifi_board.h"
#include "application.h"
#include "button.h"
#include "codecs/no_audio_codec.h"
#include "config.h"
#include "display/oled_display.h"
#include "esp32_camera.h"
#include "head_policy.h"
#include "led/single_led.h"
#include "mcp_server.h"

#include <driver/i2c_master.h>
#include <driver/ledc.h>
#include <esp_check.h>
#include <esp_lcd_panel_io.h>
#include <esp_lcd_panel_ops.h>
#include <esp_lcd_panel_sh1106.h>
#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <mutex>
#include <string>

static constexpr char kTag[] = "FamilyRobot";

class ServoHead {
public:
    void Initialize() {
        ledc_timer_config_t timer = {};
        timer.speed_mode = LEDC_LOW_SPEED_MODE;
        timer.duty_resolution = LEDC_TIMER_13_BIT;
        timer.timer_num = LEDC_TIMER_1;
        timer.freq_hz = 50;
        timer.clk_cfg = LEDC_USE_APB_CLK;
        ESP_ERROR_CHECK(ledc_timer_config(&timer));

        ConfigureChannel(LEDC_CHANNEL_2, kPanSignal);
        ConfigureChannel(LEDC_CHANNEL_3, kTiltSignal);
        if (xTaskCreate(Task, "robot-head", 3072, this, 2, nullptr) != pdPASS) {
            ESP_LOGE(kTag, "Cannot create servo worker");
            ESP_ERROR_CHECK(ESP_ERR_NO_MEM);
        }
        ESP_LOGI(kTag, "Head DISARMED; no PWM pulses. Hold head button to arm.");
    }

    bool ToggleLocally() {
        std::lock_guard<std::mutex> lock(mutex_);
        enabled_ = !enabled_;
        pan_target_ = 0;
        tilt_target_ = 0;
        ESP_LOGI(kTag, "Head %s by LOCAL button", enabled_ ? "ARMED" : "DISARMED");
        return enabled_;
    }

    void Disable() {
        std::lock_guard<std::mutex> lock(mutex_);
        enabled_ = false;
        ESP_LOGW(kTag, "Head disarmed");
    }

    ToolResult Move(int pan, int tilt) {
        if (!head_policy::ValidPosition(pan) || !head_policy::ValidPosition(tilt)) {
            ESP_LOGW(kTag, "Rejected head target: %d,%d", pan, tilt);
            return std::unexpected("Positions must be integers from -10 to 10, not degrees.");
        }
        std::lock_guard<std::mutex> lock(mutex_);
        if (!enabled_) {
            ESP_LOGW(kTag, "Rejected head movement: physical arming required");
            return std::unexpected("Head disarmed. A person must hold the physical head button.");
        }
        pan_target_ = pan;
        tilt_target_ = tilt;
        ESP_LOGI(kTag, "Head target accepted: pan=%d tilt=%d", pan, tilt);
        return ReturnValue(std::string("Target accepted; no position sensor confirms actual movement."));
    }

    std::string Status() {
        std::lock_guard<std::mutex> lock(mutex_);
        return std::string(enabled_ ? "ARMED" : "DISARMED") +
               "; pan target=" + std::to_string(pan_target_) +
               "; tilt target=" + std::to_string(tilt_target_) +
               "; coordinates -10..10 are logical positions, not degrees.";
    }

private:
    std::mutex mutex_;
    bool enabled_ = false;
    int pan_target_ = 0;
    int tilt_target_ = 0;
    int pan_us_ = head_policy::kCenterUs;
    int tilt_us_ = head_policy::kCenterUs;

    static void ConfigureChannel(ledc_channel_t channel, gpio_num_t pin) {
        ledc_channel_config_t config = {};
        config.gpio_num = pin;
        config.speed_mode = LEDC_LOW_SPEED_MODE;
        config.channel = channel;
        config.timer_sel = LEDC_TIMER_1;
        config.duty = 0;
        config.hpoint = 0;
        ESP_ERROR_CHECK(ledc_channel_config(&config));
    }

    static void WritePulse(ledc_channel_t channel, int pulse_us) {
        ESP_ERROR_CHECK(ledc_set_duty(LEDC_LOW_SPEED_MODE, channel, head_policy::Duty(pulse_us)));
        ESP_ERROR_CHECK(ledc_update_duty(LEDC_LOW_SPEED_MODE, channel));
    }

    static void Task(void* context) {
        auto& self = *static_cast<ServoHead*>(context);
        for (;;) {
            {
                std::lock_guard<std::mutex> lock(self.mutex_);
                if (self.enabled_) {
                    self.pan_us_ = head_policy::Approach(self.pan_us_,
                        head_policy::PulseUs(self.pan_target_, head_policy::kPanSign));
                    self.tilt_us_ = head_policy::Approach(self.tilt_us_,
                        head_policy::PulseUs(self.tilt_target_, head_policy::kTiltSign));
                    WritePulse(LEDC_CHANNEL_2, self.pan_us_);
                    WritePulse(LEDC_CHANNEL_3, self.tilt_us_);
                } else {
                    ESP_ERROR_CHECK(ledc_stop(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_2, 0));
                    ESP_ERROR_CHECK(ledc_stop(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_3, 0));
                    self.pan_us_ = head_policy::kCenterUs;
                    self.tilt_us_ = head_policy::kCenterUs;
                }
            }
            vTaskDelay(pdMS_TO_TICKS(20));
        }
    }
};

class FamilyRobot : public WifiBoard {
private:
    Button chat_button_{kChatButton};
    Button head_button_{kHeadButton, false, 2000};
    OledDisplay* display_ = nullptr;
    Esp32Camera* camera_ = nullptr;
    ServoHead head_;
    unsigned local_step_ = 0;

    void InitializeDisplay() {
        i2c_master_bus_config_t bus_config = {};
        bus_config.i2c_port = I2C_NUM_1;
        bus_config.sda_io_num = kOledSda;
        bus_config.scl_io_num = kOledScl;
        bus_config.clk_source = I2C_CLK_SRC_DEFAULT;
        bus_config.glitch_ignore_cnt = 7;
        bus_config.flags.enable_internal_pullup = true;
        i2c_master_bus_handle_t bus = nullptr;
        ESP_ERROR_CHECK(i2c_new_master_bus(&bus_config, &bus));

        const bool found_3c = i2c_master_probe(bus, 0x3c, 100) == ESP_OK;
        const bool found_3d = i2c_master_probe(bus, 0x3d, 100) == ESP_OK;
        if (found_3c == found_3d) {
            ESP_LOGE(kTag, "Expected one OLED at 0x3c OR 0x3d. Check power and wiring.");
            ESP_ERROR_CHECK(ESP_ERR_NOT_FOUND);
        }
        esp_lcd_panel_io_i2c_config_t io_config = {};
        io_config.dev_addr = found_3c ? 0x3c : 0x3d;
        io_config.scl_speed_hz = 400000;
        io_config.control_phase_bytes = 1;
        io_config.dc_bit_offset = 6;
        io_config.lcd_cmd_bits = 8;
        io_config.lcd_param_bits = 8;
        esp_lcd_panel_io_handle_t io = nullptr;
        ESP_ERROR_CHECK(esp_lcd_new_panel_io_i2c(bus, &io_config, &io));
        esp_lcd_panel_dev_config_t panel_config = {};
        panel_config.reset_gpio_num = GPIO_NUM_NC;
        panel_config.bits_per_pixel = 1;
        esp_lcd_panel_handle_t panel = nullptr;
        ESP_ERROR_CHECK(esp_lcd_new_panel_sh1106(io, &panel_config, &panel));
        ESP_ERROR_CHECK(esp_lcd_panel_reset(panel));
        ESP_ERROR_CHECK(esp_lcd_panel_init(panel));
        ESP_ERROR_CHECK(esp_lcd_panel_invert_color(panel, false));
        ESP_ERROR_CHECK(esp_lcd_panel_disp_on_off(panel, true));
        display_ = new OledDisplay(io, panel, 128, 64, false, false);
        ESP_LOGI(kTag, "SH1106 initialized at 0x%02x on I2C1", io_config.dev_addr);
    }

    void InitializeCamera() {
        camera_config_t c = {};
        c.pin_pwdn = -1;
        c.pin_reset = -1;
        c.pin_xclk = 10;
        c.pin_sccb_sda = 40;
        c.pin_sccb_scl = 39;
        c.pin_d7 = 48;
        c.pin_d6 = 11;
        c.pin_d5 = 12;
        c.pin_d4 = 14;
        c.pin_d3 = 16;
        c.pin_d2 = 18;
        c.pin_d1 = 17;
        c.pin_d0 = 15;
        c.pin_vsync = 38;
        c.pin_href = 47;
        c.pin_pclk = 13;
        c.sccb_i2c_port = 0;
        c.xclk_freq_hz = 20000000;
        c.ledc_timer = LEDC_TIMER_0;
        c.ledc_channel = LEDC_CHANNEL_0;
        c.pixel_format = PIXFORMAT_RGB565;
        c.frame_size = FRAMESIZE_QVGA;
        c.jpeg_quality = 12;
        c.fb_count = 1;
        c.fb_location = CAMERA_FB_IN_PSRAM;
        c.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
        camera_ = new Esp32Camera(c);
        auto sensor = esp_camera_sensor_get();
        if (sensor == nullptr) {
            ESP_LOGE(kTag, "Camera failed. Check Sense expansion and sensor model.");
            ESP_ERROR_CHECK(ESP_FAIL);
        }
        ESP_LOGI(kTag, "Camera ready; PID=0x%04x, timer0/channel0", sensor->id.PID);
    }

    void InitializeButtons() {
        chat_button_.OnClick([this]() {
            auto& app = Application::GetInstance();
            if (app.GetDeviceState() == kDeviceStateStarting) {
                EnterWifiConfigMode();
                return;
            }
            app.ToggleChatState();
        });
        chat_button_.OnLongPress([this]() {
            head_.Disable();
            EnterWifiConfigMode();
        });
        head_button_.OnLongPress([this]() {
            const bool enabled = head_.ToggleLocally();
            display_->ShowNotification(enabled ? "HEAD ARMED" : "HEAD OFF");
        });
        head_button_.OnClick([this]() {
            constexpr int positions[][2] = {
                {0, 0}, {-5, 0}, {0, 0}, {5, 0},
                {0, 0}, {0, -5}, {0, 0}, {0, 5}};
            const auto& position = positions[local_step_ % 8];
            const auto result = head_.Move(position[0], position[1]);
            if (!result) {
                display_->ShowNotification(result.error().c_str());
            } else {
                ++local_step_;
                display_->ShowNotification("LOCAL HEAD TEST");
            }
        });
    }

    void InitializeTools() {
        auto& mcp = McpServer::GetInstance();
        mcp.AddTool("self.head.move",
            "Move the lightweight head. Logical positions, NOT degrees. "
            "pan: -10 left to +10 right from the robot perspective; "
            "tilt: -10 down to +10 up. Requires prior physical arming. "
            "Use small values first. Never claim measured physical position.",
            PropertyList({
                Property("pan", kPropertyTypeInteger, -10, 10),
                Property("tilt", kPropertyTypeInteger, -10, 10)}),
            [this](const PropertyList& p) -> ToolResult {
                return head_.Move(p["pan"].value<int>(), p["tilt"].value<int>());
            });
        mcp.AddTool("self.head.status", "Read arming status and commanded targets.",
            PropertyList(), [this](const PropertyList&) -> ToolResult {
                return ReturnValue(head_.Status());
            });
        mcp.AddTool("self.head.off", "Disable servo PWM. Head may relax; support it first.",
            PropertyList(), [this](const PropertyList&) -> ToolResult {
                head_.Disable();
                return ReturnValue(true);
            });
    }

public:
    FamilyRobot() {
        InitializeDisplay();
        InitializeCamera();
        head_.Initialize();
        InitializeButtons();
        InitializeTools();
        GetAudioCodec()->SetOutputVolume(20);
    }

    AudioCodec* GetAudioCodec() override {
        static NoAudioCodecSimplexPdm codec(16000, 24000, kSpeakerBclk, kSpeakerLrck,
                                           kSpeakerData, kMicClock, kMicData);
        return &codec;
    }

    Display* GetDisplay() override { return display_; }
    Camera* GetCamera() override { return camera_; }
    Led* GetLed() override {
        static SingleLed led(GPIO_NUM_21);
        return &led;
    }
};

DECLARE_BOARD(FamilyRobot);
