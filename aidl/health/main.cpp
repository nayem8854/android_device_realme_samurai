/*
 * Copyright (c) 2022-2025 Qualcomm Innovation Center, Inc. All rights reserved.
 * Copyright (C) 2024-2026 The LineageOS Project
 * SPDX-License-Identifier: BSD-3-Clause-Clear
 */

#define LOG_TAG "android.hardware.health-service.samurai"

#include <android-base/logging.h>
#include <android-base/unique_fd.h>
#include <android/binder_interface_utils.h>
#include <cutils/klog.h>
#include <cutils/properties.h>
#include <cutils/uevent.h>
#include <fcntl.h>
#include <health-impl/ChargerUtils.h>
#include <health-impl/HalHealthLoop.h>
#include <health-impl/Health.h>
#include <health/utils.h>
#include <healthd/healthd.h>
#include <string.h>
#include <unistd.h>

using aidl::android::hardware::health::HalHealthLoop;
using aidl::android::hardware::health::Health;

#if !CHARGER_FORCE_NO_UI
using aidl::android::hardware::health::charger::ChargerCallback;
using aidl::android::hardware::health::charger::ChargerModeMain;
namespace aidl::android::hardware::health {
class ChargerCallbackImpl : public ChargerCallback {
  public:
    ChargerCallbackImpl(const std::shared_ptr<Health>& service) : ChargerCallback(service) {}
    bool ChargerEnableSuspend() override { return true; }
};
} // namespace aidl::android::hardware::health
#endif

static constexpr const char* gInstanceName = "default";
static constexpr std::string_view gChargerArg{"--charger"};

static constexpr std::array<std::string_view, 3> ucsiPSYNames = {
    "ucsi-source-psy-soc:qcom,pmic_glink:qcom,ucsi1",
    "ucsi-source-psy-soc:qcom,pmic_glink:qcom,ucsi2",
    "ucsi-source-psy-soc:pmic-glink:ucsi-glink1"
};

#define BMS_SYSFS_PATH "/sys/class/power_supply/bms/"
#define BATTERY_SYSFS_PATH "/sys/class/power_supply/battery/"

#define RETRY_COUNT 100

// OPLUS_CHG (drivers/power/oppo/charger_ic/oplus_battery_msm8150Q.c) exports
// ~90 power_supply properties on "battery" and bumps kernel UEVENT_BUFFER_SIZE
// to 4096 (include/linux/kobject.h). Standard AOSP libhealthloop uses a 2048-byte
// buffer (HealthLoop::kUeventMsgLen = 2048), causing recvmsg() in libcutils to
// flag MSG_TRUNC and drop every battery uevent. We register a 4096-byte uevent
// socket on HalHealthLoop so battery uevents are received and processed in real time.
static constexpr size_t kSamuraiUeventMsgLen = 4096;
static constexpr int kUeventSocketRcvbufSize = 64 * 1024;

static void SetPathIfExist(android::String8* var, const char* path) {
    if (!access(path, R_OK)) {
        *var = path;
    }
}

class SamuraiHealth : public Health {
  public:
    using Health::Health;
    virtual ~SamuraiHealth() = default;

  protected:
    void OnInit(HalHealthLoop* hal_health_loop, struct healthd_config* config) override {
        Health::OnInit(hal_health_loop, config);

        uevent_fd_.reset(uevent_open_socket(kUeventSocketRcvbufSize, true));
        if (uevent_fd_.get() < 0) {
            KLOG_ERROR(LOG_TAG, "SamuraiHealth: uevent_open_socket failed, errno=%d\n", errno);
            return;
        }
        fcntl(uevent_fd_.get(), F_SETFL, O_NONBLOCK);

        if (hal_health_loop->RegisterEvent(
                uevent_fd_.get(),
                [this](auto*, uint32_t epevents) { UeventEvent4096(epevents); },
                EVENT_WAKEUP_FD) != 0) {
            KLOG_ERROR(LOG_TAG, "SamuraiHealth: RegisterEvent for 4096-byte uevent socket failed\n");
        } else {
            KLOG_INFO(LOG_TAG, "SamuraiHealth: Registered 4096-byte uevent socket for OPLUS_CHG\n");
        }
    }

  private:
    void UeventEvent4096(uint32_t /*epevents*/) {
        char msg[kSamuraiUeventMsgLen + 2];
        char* cp;
        ssize_t n;

        n = uevent_kernel_multicast_recv(uevent_fd_.get(), msg, kSamuraiUeventMsgLen);
        if (n <= 0) return;
        if (static_cast<size_t>(n) >= kSamuraiUeventMsgLen) {
            return;
        }

        msg[n] = '\0';
        msg[n + 1] = '\0';
        cp = msg;

        while (*cp) {
            if (!strcmp(cp, "SUBSYSTEM=power_supply")) {
                this->update();
                break;
            }
            while (*cp++)
                ;
        }
    }

    ::android::base::unique_fd uevent_fd_;
};

void qti_healthd_board_init(struct healthd_config* hc) {
    FILE* fp = NULL;
    int fd;
    unsigned char retries = RETRY_COUNT;
    int ret = 0;
    unsigned char buf;

    hc->ignorePowerSupplyNames.push_back(android::String8(ucsiPSYNames[0].data()));
    hc->ignorePowerSupplyNames.push_back(android::String8(ucsiPSYNames[1].data()));
    hc->ignorePowerSupplyNames.push_back(android::String8(ucsiPSYNames[2].data()));

    SetPathIfExist(&hc->batteryFullChargeDesignCapacityUahPath,
                   BMS_SYSFS_PATH "charge_full_design");
    SetPathIfExist(&hc->batteryFullChargeDesignCapacityUahPath,
                   BATTERY_SYSFS_PATH "charge_full_design");
    SetPathIfExist(&hc->batteryFullChargePath, BMS_SYSFS_PATH "charge_full");
    SetPathIfExist(&hc->batteryFullChargePath, BATTERY_SYSFS_PATH "charge_full");
    SetPathIfExist(&hc->batteryCycleCountPath, BMS_SYSFS_PATH "cycle_count");
    SetPathIfExist(&hc->batteryCycleCountPath, BATTERY_SYSFS_PATH "cycle_count");
    SetPathIfExist(&hc->batteryChargeTimeToFullNowPath,
                   BMS_SYSFS_PATH "time_to_full_now");
    SetPathIfExist(&hc->batteryChargeTimeToFullNowPath,
                   BATTERY_SYSFS_PATH "time_to_full_now");
    if (!access(BMS_SYSFS_PATH "voltage_ocv", R_OK)) {
        hc->batteryVoltagePath = BMS_SYSFS_PATH "voltage_ocv";
    }

retry:
    if (!retries) {
        KLOG_ERROR(LOG_TAG, "Cannot open battery/capacity, fd=%d\n", fd);
        return;
    }

    fd = open("/sys/class/power_supply/battery/capacity", 0440);
    if (fd >= 0) {
        KLOG_INFO(LOG_TAG, "opened battery/capacity after %d retries\n", RETRY_COUNT - retries);
        while (retries) {
            ret = read(fd, &buf, 1);
            if (ret >= 0) {
                KLOG_INFO(LOG_TAG, "Read Batt Capacity after %d retries ret : %d\n", RETRY_COUNT - retries, ret);
                close(fd);
                return;
            }

            retries--;
            usleep(100000);
        }

        KLOG_ERROR(LOG_TAG, "Failed to read Battery Capacity ret=%d\n", ret);
        close(fd);
        return;
    }

    retries--;
    usleep(100000);
    goto retry;
}

int main(int argc, char** argv) {
#ifdef __ANDROID_RECOVERY__
    android::base::InitLogging(argv, android::base::KernelLogger);
#endif

    auto config = std::make_unique<healthd_config>();
    ::android::hardware::health::InitHealthdConfig(config.get());
    qti_healthd_board_init(config.get());

    // Native periodic chores fallback alongside 4096-byte uevent listener
    config->periodic_chores_interval_fast = 20;
    config->periodic_chores_interval_slow = 60;

    auto binder = ndk::SharedRefBase::make<SamuraiHealth>(gInstanceName, std::move(config));

    if (argc >= 2 && argv[1] == gChargerArg) {
#if !CHARGER_FORCE_NO_UI
        KLOG_INFO(LOG_TAG, "Starting charger mode with UI.");
        auto charger_callback = std::make_shared<aidl::android::hardware::health::ChargerCallbackImpl>(binder);
        return ChargerModeMain(binder, charger_callback);
#endif
        KLOG_INFO(LOG_TAG, "Starting charger mode without UI.");
    } else {
        KLOG_INFO(LOG_TAG, "Starting health HAL.");
    }

    auto hal_health_loop = std::make_shared<HalHealthLoop>(binder, binder);
    return hal_health_loop->StartLoop();
}
