#!/bin/bash
#
# Copyright (C) 2018-2019 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

set -e

DEVICE=RMX1931
VENDOR=realme

# Load extract_utils and do some sanity checks
MY_DIR="${BASH_SOURCE%/*}"
if [[ ! -d "${MY_DIR}" ]]; then MY_DIR="${PWD}"; fi

LINEAGE_ROOT="${MY_DIR}"/../../..

HELPER="${LINEAGE_ROOT}/vendor/lineage/build/tools/extract_utils.sh"
if [ ! -f "${HELPER}" ]; then
    echo "Unable to find helper script at ${HELPER}"
    exit 1
fi
source "${HELPER}"

SECTION=
KANG=

while [ "${#}" -gt 0 ]; do
    case "${1}" in
        -n | --no-cleanup )
                CLEAN_VENDOR=false
                ;;
        -k | --kang )
                KANG="--kang"
                ;;
        -s | --section )
                SECTION="${2}"; shift
                CLEAN_VENDOR=false
                ;;
        * )
                SRC="${1}"
                ;;
    esac
    shift
done

if [ -z "${SRC}" ]; then
    SRC="adb"
fi

function blob_fixup() {
    case "${1}" in
        system_ext/etc/init/dpmd.rc)
            sed -i "s/\/system\/product\/bin\//\/system\/system_ext\/bin\//g" "${2}"
            ;;
        system_ext/etc/permissions/com.qti.dpmframework.xml)
            ;&
        system_ext/etc/permissions/dpmapi.xml)
            ;&
        system_ext/etc/permissions/qcrilhook.xml)
            ;&
        system_ext/etc/permissions/telephonyservice.xml)
            sed -i "s/\/product\/framework\//\/system_ext\/framework\//g" "${2}"
            ;;
        system_ext/etc/permissions/qti_libpermissions.xml)
            sed -i "s/name=\"android.hidl.manager-V1.0-java/name=\"android.hidl.manager@1.0-java/g" "${2}"
            ;;
        etc/permissions/qti_libpermissions.xml)
            sed -i 's|name="android.hidl.manager-V1.0-java"|name="android.hidl.manager@1.0-java"|g' "${2}"
            ;;
        product/lib64/libdpmframework.so)
            patchelf --add-needed "libshim_dpmframework.so" "${2}"
            ;;
    esac
}

# Initialize the helper
setup_vendor "${DEVICE}" "${VENDOR}" "${LINEAGE_ROOT}" true "${CLEAN_VENDOR}"

extract "${MY_DIR}/proprietary-files.txt" "${SRC}" \
        "${KANG}" --section "${SECTION}"

"${MY_DIR}/setup-makefiles.sh"
