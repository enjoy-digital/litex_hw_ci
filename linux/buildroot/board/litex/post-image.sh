#!/bin/bash
set -euo pipefail

# Define paths.
BOARD_DIR="$(dirname "$0")"
GENIMAGE_CFG="${BOARD_DIR}/genimage.cfg"
GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
LINUX_ON_LITEX_DIR="${BR2_EXTERNAL_LITEX_PATH}/../images"

# Define binary destinations.
DST_DTB="${LINUX_ON_LITEX_DIR}/soc.dtb"
DST_OPENSBI="${LINUX_ON_LITEX_DIR}/opensbi.bin"
DST_IMAGE="${LINUX_ON_LITEX_DIR}/Image"
DST_ROOTFS="${LINUX_ON_LITEX_DIR}/rootfs.cpio"

# Force-create symlinks to binaries.
ln -sf "${BINARIES_DIR}/fw_jump.bin" "${DST_OPENSBI}"
ln -sf "${BINARIES_DIR}/Image" "${DST_IMAGE}"
ln -sf "${BINARIES_DIR}/rootfs.cpio" "${DST_ROOTFS}"

# Check DTB presence, create dummy if absent.
if [ ! -e "${DST_DTB}" ]; then
    echo -e "\nWarning: ${DST_DTB} missing. A dummy file is created, replace with actual soc.dtb.\n"
    touch "${DST_DTB}"
fi

# Setup and cleanup temporary directories for genimage.
ROOTPATH_TMP="$(mktemp -d)"
trap 'rm -rf "${ROOTPATH_TMP}" "${GENIMAGE_TMP}"' EXIT

# Execute genimage.
genimage \
    --rootpath "${ROOTPATH_TMP}" \
    --tmppath "${GENIMAGE_TMP}" \
    --inputpath "${LINUX_ON_LITEX_DIR}" \
    --outputpath "${LINUX_ON_LITEX_DIR}" \
    --config "${GENIMAGE_CFG}"
