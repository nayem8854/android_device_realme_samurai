#!/usr/bin/env bash
#
# Clone device tree dependencies when missing (Infinity-X / roomservice helper).
# Paths match lineage.dependencies.
#

B="\033[1;34m"
G="\033[1;32m"
R="\033[1;31m"
N="\033[0m"

SRC_DIR="${PWD}"

OPLUS_DIR="${SRC_DIR}/hardware/oplus"
OPLUS_REPO="https://github.com/LineageOS/android_hardware_oplus"
OPLUS_BRANCH="lineage-23.2"

DOLBY_DIR="${SRC_DIR}/vendor/lunaris/dolby"
DOLBY_REPO="https://github.com/tranQuila-Project/vendor_lunaris_dolby"
DOLBY_BRANCH="main"

clone_if_missing() {
    local dir="$1"
    local repo="$2"
    local branch="$3"
    local name="$4"

    if [ -d "${dir}/.git" ] || [ -d "${dir}" ]; then
        echo -e "${G}${name} found at ${dir}${N}"
        return 0
    fi

    echo -e "${R}${name} not found${N}"
    echo -e "${B}Cloning ${name} (${branch})...${N}"
    if git clone --depth=1 -b "${branch}" "${repo}" "${dir}"; then
        echo -e "${G}Successfully cloned ${name}${N}"
    else
        echo -e "${R}Failed to clone ${name} from ${repo}${N}"
        return 1
    fi
}

echo -e "${B}samurai: checking device dependencies...${N}"
clone_if_missing "${OPLUS_DIR}" "${OPLUS_REPO}" "${OPLUS_BRANCH}" "hardware/oplus"
clone_if_missing "${DOLBY_DIR}" "${DOLBY_REPO}" "${DOLBY_BRANCH}" "LunarisAOSP Dolby Atmos"
