#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

import os

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)
from extract_utils.tools import (
    patchelf_version_path_map,
)
from extract_utils.utils import (
    run_cmd,
)

namespace_imports = [
    'device/realme/samurai',
    'hardware/oplus',
    'hardware/qcom-caf/sm8150',
    'hardware/qcom-caf/wlan',
    'vendor/qcom/opensource/commonsys/display',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/dataservices',
    'vendor/qcom/opensource/display',
]


def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'com.qualcomm.qti.dpm.api@1.0',
        'libmmosal',
        'vendor.qti.hardware.fm@1.0',
        'vendor.qti.imsrtpservice@3.0',
        'vendor.qti.hardware.wifidisplaysession@1.0',
    ): lib_fixup_vendor_suffix,
}


def mpbase_use_padding_shim(ctx, file, file_path, *args, **kwargs):
    # Route libmpbase's malloc/realloc through libmpbase_shim, which pads
    # large allocations (the refocus engine reads past their end).
    syms = f'{file_path}.syms'
    with open(syms, 'w') as f:
        f.write('malloc mpbase_shim_malloc\nrealloc mpbase_shim_realloc\n')
    run_cmd([patchelf_version_path_map['0_18'], '--rename-dynamic-symbols', syms, file_path])
    os.remove(syms)


blob_fixups: blob_fixups_user_type = {
    (
        'odm/etc/init/android.hardware.drm@1.3-service.widevine.rc',
        'vendor/etc/init/vendor.qti.media.c2@1.0-service.rc',
    ): blob_fixup()
        .regex_replace('writepid /dev/cpuset/foreground/tasks', 'task_profiles ProcessCapacityHigh'),
    'odm/lib64/libgf_hal_G3.so': blob_fixup()
        .binary_regex_replace(b'/sys/kernel/oplus_display/', b'/sys/kernel//oppo_display/'),
    'odm/lib64/libmpbase.so': blob_fixup()
        .call(mpbase_use_padding_shim)
        .add_needed('libmpbase_shim.so'),
    'odm/lib64/libsnpe_dsp_domains_v2.so': blob_fixup()
        .clear_symbol_version('remote_handle64_close')
        .clear_symbol_version('remote_handle64_control')
        .clear_symbol_version('remote_handle64_invoke')
        .clear_symbol_version('remote_handle64_open')
        .clear_symbol_version('remote_register_buf')
        .clear_symbol_version('remote_register_buf_attr')
        .clear_symbol_version('remote_register_dma_handle'),
    (
        'odm/lib/mediadrm/libwvdrmengine.so',
        'odm/lib64/mediadrm/libwvdrmengine.so',
        'odm/lib64/libwvhidl.so',
    ): blob_fixup()
        .replace_needed('libcrypto.so', 'libcryp_s.so'),
    (
        'system_ext/etc/permissions/qcrilhook.xml',
        'system_ext/etc/permissions/qti_libpermissions.xml',
    ): blob_fixup()
        .regex_replace('name="android.hidl.manager-V1.0-java', 'name="android.hidl.manager@1.0-java'),
    'vendor/etc/init/android.hardware.neuralnetworks@1.3-service-qti.rc': blob_fixup()
        .regex_replace('writepid /dev/stune/nnapi-hal/tasks', 'task_profiles NNApiHALPerformance'),
    (
        'vendor/etc/seccomp_policy/atfwd@2.0.policy',
        'vendor/etc/seccomp_policy/wfdhdcphalservice.policy',
    ): blob_fixup()
        .add_line_if_missing('gettid: 1'),
    'vendor/etc/seccomp_policy/vendor.qti.hardware.dsp.policy': blob_fixup()
        .add_line_if_missing('madvise: 1'),
    'vendor/etc/wfdconfig.xml': blob_fixup()
        .regex_replace('<AudioStreamInSuspend>0</AudioStreamInSuspend>', '<AudioStreamInSuspend>1</AudioStreamInSuspend>')
        .regex_replace('<HID>0</HID>', '<HID>1</HID>'),
    'vendor/lib64/hw/camera.qcom.so': blob_fixup()
        .add_needed('libcamera_metadata_shim.so'),
    (
        'vendor/lib64/libCOppLceTonemapAPI.so',
        'vendor/lib64/libOPPORectify.so',
    ): blob_fixup()
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so'),
    'vendor/lib64/libOGLManager.so': blob_fixup()
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock'),
    (
        'odm/lib64/libVDBlurless.so',
        'odm/lib64/libVDBlurlessAPI_v2.so',
        'vendor/lib64/libarcsoft_dualcam_refocus_preview.so',
    ): blob_fixup()
        .clear_symbol_version('remote_handle_close')
        .clear_symbol_version('remote_handle_invoke')
        .clear_symbol_version('remote_handle_open')
        .clear_symbol_version('remote_register_buf')
        .clear_symbol_version('remote_register_buf_attr'),
    'vendor/lib64/libarcsoft_hdrplus_hvx_5221_stub.so': blob_fixup()
        .clear_symbol_version('remote_handle64_close')
        .clear_symbol_version('remote_handle64_invoke')
        .clear_symbol_version('remote_handle64_open')
        .clear_symbol_version('remote_register_buf')
        .clear_symbol_version('remote_register_buf_attr'),
    'vendor/lib64/libdpps.so': blob_fixup()
        .replace_needed('libtinyxml2.so', 'libtinyxml2-v34.so'),
    'vendor/lib64/libhvx_proxy_stub.so': blob_fixup()
        .clear_symbol_version('remote_handle64_close')
        .clear_symbol_version('remote_handle64_invoke')
        .clear_symbol_version('remote_handle64_open')
        .clear_symbol_version('remote_register_dma_handle')
        .clear_symbol_version('remote_register_dma_handle_attr'),
}  # fmt: skip

module = ExtractUtilsModule(
    'samurai',
    'realme',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
    check_elf=False,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
