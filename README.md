Clone this repo first:

```
git clone https://github.com/ant9000/nina-micropython
cd nina-micropython
```

Clone my Micropython repo:

```
git clone https://github.com/ant9000/micropython --branch updated_libhydrogen
```

Activate Zephyr environment and compile:

```
source ~/zephyrproject/.venv/bin/activate
./build.sh
```

To flash the board:

```
./flash.sh
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
