#!/bin/bash -e

cd $(dirname $0)
BASE=`pwd`
TARGET=${BASE}/build

which west || {
  echo "West command not found - please activate Zephyr environment"
  exit 1
}

cd $(dirname $(which west))
cd $(west topdir)

CFLAGS="-DMICROPY_CONFIG_ROM_LEVEL=MICROPY_CONFIG_ROM_LEVEL_EXTRA_FEATURES"
CFLAGS="$CFLAGS -DMICROPY_PY_MACHINE_DISABLE_IRQ_ENABLE_IRQ=1"
CFLAGS="$CFLAGS -DMICROPY_PY_MACHINE_BITSTREAM"
CFLAGS="$CFLAGS -DMODULE_HYDROGEN_ENABLED=1"
CFLAGS="$CFLAGS -DSTATIC=static"

west build -b ubx_evkninab3 \
    -d $TARGET \
    $BASE/micropython/ports/zephyr/ \
    -DEXTRA_CONF_FILE=$BASE/nina.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$BASE/nina.overlay \
    -DEXTRA_ZEPHYR_MODULES=$BASE/nina \
    -DUSER_C_MODULES=${BASE}/modules/ \
    -DEXTRA_CFLAGS="$CFLAGS" \
    $*
