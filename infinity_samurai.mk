#
# Copyright (C) 2020 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

$(call inherit-product, device/realme/samurai/device.mk)

# Inherit some common Infinity stuff.
$(call inherit-product, vendor/infinity/config/common_full_phone.mk)

# Device identifier. This must come after all inclusions.
PRODUCT_BRAND := realme
PRODUCT_DEVICE := samurai
PRODUCT_MANUFACTURER := realme
PRODUCT_MODEL := realme X2 Pro
PRODUCT_NAME := infinity_samurai

BUILD_FINGERPRINT := realme/RMX1931/RMX1931L1:11/RKQ1.200928.002/1625457120608:user/release-keys

PRODUCT_BUILD_PROP_OVERRIDES += \
    BuildDesc="RMX1931-user 11 RKQ1.200928.002 1625457120608 release-keys" \
    BuildFingerprint=realme/RMX1931/RMX1931L1:11/RKQ1.200928.002/1625457120608:user/release-keys \
    DeviceName=RMX1931L1 \
    DeviceProduct=RMX1931 \
    SystemDevice=RMX1931L1 \
    SystemName=RMX1931

PRODUCT_GMS_CLIENTID_BASE := android-oppo

# Infinity-X
TARGET_HAS_UDFPS := true
TARGET_SUPPORTS_QUICK_TAP := true
TARGET_SUPPORTS_BLUR := true

# GApps defaults; override WITH_GAPPS=false at lunch for vanilla builds.
WITH_GAPPS := false
ifeq ($(WITH_GAPPS),true)
TARGET_BUILD_GOOGLE_TELEPHONY := true
TARGET_SHIPS_FULL_GAPPS := true
endif

INFINITY_MAINTAINER := NAYEM
