Clone this repo first:

```
git clone https://github.com/ant9000/nina-micropython
cd nina-micropython
```

Define `BASE` as current dir:

```
BASE=`pwd`
```

Clone Micropython repo:

```
git clone https://github.com/micropython/micropython
```

Move to Zephyr installation and compile:

```
cd ~/zephyrproject/zephyr
west build -b ubx_evkninab3 \
    -d ~/zephyrproject/nina-micropython \
    $BASE/micropython/ports/zephyr/ \
    -DEXTRA_CONF_FILE=$BASE/nina.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$BASE/nina.overlay \
    -DEXTRA_CFLAGS="-DMICROPY_CONFIG_ROM_LEVEL=MICROPY_CONFIG_ROM_LEVEL_EXTRA_FEATURES -DMICROPY_PY_MACHINE_BITSTREAM"
```

For further work, just move to the build directory:

```
cd ~/zephyrproject/nina-micropython/
west flash --runner pyocd
```

(assuming you have a pyOCD compatible programmer, for instance a FreeDAP one).

For a complete Micropython IDE, you can install Thonny:

```
sudo apt install pipx python3-pyserial
pipx install thonny
```

and then simply launch it as

```
thonny
```
