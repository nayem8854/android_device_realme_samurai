#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils:../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixup_remove,
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'device/realme/samurai',
    'hardware/oplus',
    'hardware/qcom-caf/common/libqti-perfd-client',
    'hardware/qcom-caf/sm8150',
    'hardware/qcom-caf/wlan',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/commonsys/display',
    'vendor/qcom/opensource/dataservices',
    'vendor/qcom/opensource/display',
]


def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'com.qualcomm.qti.dpm.api@1.0',
        'libstdc++',
        'vendor.qti.hardware.fm@1.0',
        'vendor.qti.hardware.wifidisplaysession@1.0',
        'vendor.qti.imsrtpservice@3.0',
    ): lib_fixup_vendor_suffix,
    (
        'libPolarrRender',
        'libQTEEConnector_system',
        'libbluetooth_audio_session_qti_2_1',
        'libbsproxy',
        'libml_util',
        'libmmparser_lite',
        'libxtwifi_server_protocol',
        'libxtwifi_server_protocol_uri_v3',
        'vendor.qti.hardware.cacert@1.0',
        'vendor.qti.hardware.improvetouch.touchcompanion@1.0',
        'vendor.qti.qspmhal@1.0',
    ): lib_fixup_remove,
}

blob_fixups: blob_fixups_user_type = {
    ('vendor/lib64/libOPPORectify.so', 'vendor/lib64/libCOppLceTonemapAPI.so'): blob_fixup()
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so'),
    'vendor/lib64/libOGLManager.so': blob_fixup()
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock'),
    ('odm/lib64/mediadrm/libwvdrmengine.so', 'odm/lib/mediadrm/libwvdrmengine.so'): blob_fixup()
        .add_needed('libcrypto_shim.so'),
    'vendor/lib64/hw/com.qti.chi.override.so': blob_fixup()
        .add_needed('libcamera_metadata_shim.so'),
    ('odm/lib64/libVDBlurlessAPI_v2.so', 'vendor/lib64/libarcsoft_dualcam_refocus_preview.so', 'vendor/lib64/libarcsoft_super_night_raw.so'): blob_fixup()
        .clear_symbol_version('remote_handle_close')
        .clear_symbol_version('remote_handle_invoke')
        .clear_symbol_version('remote_handle_open')
        .clear_symbol_version('remote_register_buf_attr')
        .clear_symbol_version('remote_register_buf'),
    ('vendor/lib64/libarcsoft_hdrplus_hvx_5221_stub.so', 'vendor/lib64/libhvx_proxy_stub.so'): blob_fixup()
        .clear_symbol_version('remote_handle64_close')
        .clear_symbol_version('remote_handle64_invoke')
        .clear_symbol_version('remote_handle64_open')
        .clear_symbol_version('remote_register_buf_attr')
        .clear_symbol_version('remote_register_buf')
        .clear_symbol_version('remote_register_dma_handle')
        .clear_symbol_version('remote_register_dma_handle_attr'),
    'odm/lib64/libsnpe_dsp_domains_v2.so': blob_fixup()
        .clear_symbol_version('remote_handle64_close')
        .clear_symbol_version('remote_handle64_invoke')
        .clear_symbol_version('remote_handle64_open')
        .clear_symbol_version('remote_handle64_control')
        .clear_symbol_version('remote_register_buf')
        .clear_symbol_version('remote_register_buf_attr')
        .clear_symbol_version('remote_register_dma_handle'),
    'system_ext/lib64/lib-imsvideocodec.so': blob_fixup()
        .clear_symbol_version('ANativeWindow_setBuffersTransform'),
    'system_ext/lib64/libwfdclient.so': blob_fixup()
        .clear_symbol_version('ANativeWindow_release')
        .clear_symbol_version('ANativeWindow_acquire'),
    ('vendor/lib64/libdlbdsservice.so', 'vendor/lib/libstagefright_soft_ac4dec.so', 'vendor/lib/libstagefright_soft_ddpdec.so'): blob_fixup()
        .replace_needed('libstagefright_foundation.so', 'libstagefright_foundation-v33.so'),
    'vendor/etc/sensors/sns_reg_config': blob_fixup()
        .regex_replace('version=8', 'version=9'),
    'vendor/etc/libnfc-nci.conf': blob_fixup()
        .regex_replace('NFC_DEBUG_ENABLED=0x01', 'NFC_DEBUG_ENABLED=0x00'),
    'vendor/etc/libnfc-nxp.conf': blob_fixup()
        .regex_replace('NXP_NFC_DEV_NODE="/dev/pn553"', 'NXP_NFC_DEV_NODE="/dev/nq-nci"')
        .regex_replace('(NXPLOG_.*_LOGLEVEL)=0x03', '\\1=0x02')
        .regex_replace('NFC_DEBUG_ENABLED=0x01', 'NFC_DEBUG_ENABLED=0x00')
        .regex_replace('NXP_RF_CONF_BLK_2=', '#NXP_RF_CONF_BLK_2=')
        .regex_replace('NXP_RF_CONF_BLK_3=', '#NXP_RF_CONF_BLK_3=')
        .regex_replace('NXP_RF_CONF_MAX_NUM=3', 'NXP_RF_CONF_MAX_NUM=1'),
    'vendor/etc/wfdconfig.xml': blob_fixup()
        .regex_replace('<AudioStreamInSuspend>0</AudioStreamInSuspend>', '<AudioStreamInSuspend>1</AudioStreamInSuspend>')
        .regex_replace('<HID>0</HID>', '<HID>1</HID>'),
    'system_ext/lib64/libwfdservice.so': blob_fixup()
        .replace_needed('android.media.audio.common.types-V4-cpp.so', 'android.media.audio.common.types-V5-cpp.so'),
    'vendor/etc/faceunlock/resources.zip': blob_fixup()
        .patch_file('blob-patches/OPFaceUnlock.py'),
}  # fmt: skip

module = ExtractUtilsModule(
    'samurai',
    'realme',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
