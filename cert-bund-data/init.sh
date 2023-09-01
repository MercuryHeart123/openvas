#!/bin/sh
set -e

rm -f "${STATE_FILE}"

cat "${STORAGE_PATH}/COPYING.CERT-BUND"

echo -n -e "\nCopying CERT-Bund data... "

if [ -z "$(ls -A ${MOUNT_PATH})" ]; then
    # slightly adjusted rm. The whole directory must not be deleted because it
    # containts also the dfn-cert data files
    rm -rf "${MOUNT_PATH}/"CB-*
    cp -r "${STORAGE_PATH}/"* "${MOUNT_PATH}"

    state_dir=$(dirname ${STATE_FILE})
    mkdir -p "${state_dir}"
    touch "${STATE_FILE}"

    echo "files copied."
else
    echo "nothing to do."
fi

if [ -n "${KEEP_ALIVE}" ]; then
    sleep infinity
fi
