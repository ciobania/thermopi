# ThermoPi

ThermoPi is a smart thermostat using RPi Zero 2 W

## Configuration
- background details on how I debugged this [here](https://github.com/notro/fbtft/issues/583)
- install overlay for touchscreen ads7846 from [here](https://github.com/raspberrypi/linux/blob/rpi-5.15.y/arch/arm/boot/dts/overlays/ads7846-overlay.dts)
- calibrate touchscreen:
  ```
  TSLIB_TSDEVICE=/dev/input/event0 TSLIB_CALIBFILE=/etc/pointercal TSLIB_CONFFILE=/etc/ts.conf ts_calibrate
  ```
## Installation
Create virtual environment using `system-site-packages`; this ensures we are inheriting RPi.GPIO as well.
```code()
python3 -m venv .venv --system-site-packages
```

In your project's virtual environment
```code()
sudo apt install python3-pip python3-distutils-extra python3-wheel python3-setuptools RPi.GPIO

python3 -m pip install wheel
poetry add thermopi
```
or if using pip directly
```code()
python -m pip install thermopi
```

## Usage
- can be started using systemctl
- can be started using python directly
      


## Testing
- run `make test` to run test and check if installation is done correctly
- after creating your file you can use the plugin as:
```code()
python -m thermopi
```

- install bullseye headless
- install libsdl packages 
- add details about compiling SDL2 pygame
- change hostname and user to thermostat@thermopi
- change package name to smart_pi_thermostat or leave it to thermopi
- git clone thermopi
- cd thermopi
- make clean build-install
- add line into /etc/xdg/openbox/autostart
  - DISPLAY=:0.0 python3 -m thermopi.ui.menu.homepage.homepage 2>&1 | tee $HOME/output_pygame_startx.txt_
- sudo reboot
- 