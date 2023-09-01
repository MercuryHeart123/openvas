#!/bin/sh
set -e

rm -f "${STATE_FILE}"

cat "${STORAGE_PATH}/LICENSE"

echo -n -e "\nCopying report formats... "

if [ -z "$(ls -A ${MOUNT_PATH})" ]; then
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
