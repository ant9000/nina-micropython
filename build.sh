#!/bin/bash

cd $(dirname $0)
BASE=`pwd`
TARGET=${BASE}/build

which west || {
  echo "West command not found - please activate Zephyr environment"
  exit 1
}

cd $(dirname $(which west))
cd $(west topdir)

west build -b ubx_evkninab3 \
    -d $TARGET \
    $BASE/micropython/ports/zephyr/ \
    -DEXTRA_CONF_FILE=$BASE/nina.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$BASE/nina.overlay \
    -DEXTRA_ZEPHYR_MODULES=$BASE/nina \
    -DEXTRA_CFLAGS="-DMICROPY_CONFIG_ROM_LEVEL=MICROPY_CONFIG_ROM_LEVEL_EXTRA_FEATURES -DMICROPY_PY_MACHINE_BITSTREAM" \
    $*
