# Raspberry Pi 4 Model B Technical Guide

## Overview
The Raspberry Pi 4 Model B is the latest product in the popular Raspberry Pi range of computers. It offers ground-breaking increases in processor speed, multimedia performance, memory, and connectivity compared to the prior-generation Raspberry Pi 3 Model B+.

## Technical Specifications
- Processor: Broadcom BCM2711, Quad core Cortex-A72 (ARM v8) 64-bit SoC @ 1.5GHz
- Memory: 2GB, 4GB or 8GB LPDDR4-3200 SDRAM
- Connectivity: 2.4 GHz and 5.0 GHz IEEE 802.11ac wireless, Bluetooth 5.0, BLE
- GPIO: 40-pin GPIO header (backwards compatible with previous boards)
- Video & Audio: 2 × micro-HDMI ports (up to 4Kp60 supported), 2-lane MIPI DSI display port, 2-lane MIPI CSI camera port, 4-pole stereo audio and composite video port
- Multimedia: H.265 (4Kp60 decode), H.264 (1080p60 decode, 1080p30 encode), OpenGL ES 3.0 graphics
- Storage: Micro-SD card slot for loading operating system and data storage
- USB: 2 × USB 3.0 ports, 2 × USB 2.0 ports
- Ethernet: Gigabit Ethernet
- Power: 5V DC via USB-C connector (minimum 3A), 5V DC via GPIO header, Power over Ethernet (PoE) capable

## GPIO Pin Layout
The Raspberry Pi 4 has a 40-pin GPIO header with the following pin assignments:

### Power Pins
- 3.3V: Pins 1, 17
- 5V: Pins 2, 4
- Ground: Pins 6, 9, 14, 20, 25, 30, 34, 39

### GPIO Pins
- GPIO 2 (SDA): Pin 3
- GPIO 3 (SCL): Pin 5
- GPIO 4: Pin 7
- GPIO 14 (TXD): Pin 8
- GPIO 15 (RXD): Pin 10
- GPIO 17: Pin 11
- GPIO 18 (PWM): Pin 12
- GPIO 27: Pin 13
- GPIO 22: Pin 15
- GPIO 23: Pin 16
- GPIO 24: Pin 18
- GPIO 10 (MOSI): Pin 19
- GPIO 9 (MISO): Pin 21
- GPIO 25: Pin 22
- GPIO 11 (SCLK): Pin 23
- GPIO 8 (CE0): Pin 24
- GPIO 7 (CE1): Pin 26

## Operating System Installation
1. Download Raspberry Pi Imager from official website
2. Insert micro-SD card (minimum 8GB recommended)
3. Select OS image (Raspberry Pi OS recommended for beginners)
4. Write image to SD card
5. Insert SD card into Pi and power on

## Basic Configuration
### Enable SSH
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

### Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### Configure GPIO
```bash
sudo raspi-config
```

## Programming Languages
### Python (Recommended)
```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

while True:
    GPIO.output(18, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(18, GPIO.LOW)
    time.sleep(1)
```

### C/C++
```c
#include <wiringPi.h>

int main() {
    wiringPiSetup();
    pinMode(1, OUTPUT);
    
    while(1) {
        digitalWrite(1, HIGH);
        delay(1000);
        digitalWrite(1, LOW);
        delay(1000);
    }
    return 0;
}
```

## Common Interfaces
### I2C
- Enable: `sudo raspi-config` → Interface Options → I2C
- Pins: SDA (GPIO 2), SCL (GPIO 3)
- Tools: `i2cdetect`, `i2cget`, `i2cset`

### SPI
- Enable: `sudo raspi-config` → Interface Options → SPI
- Pins: MOSI (GPIO 10), MISO (GPIO 9), SCLK (GPIO 11), CE0 (GPIO 8), CE1 (GPIO 7)

### UART
- Enable: `sudo raspi-config` → Interface Options → Serial
- Pins: TXD (GPIO 14), RXD (GPIO 15)

## Troubleshooting
### Boot Issues
- Check SD card integrity
- Verify power supply (minimum 3A for Pi 4)
- Check HDMI connections
- Look for rainbow screen (undervoltage indicator)

### Network Issues
- Check WiFi credentials in `/etc/wpa_supplicant/wpa_supplicant.conf`
- Verify Ethernet cable connection
- Check router settings and firewall

### GPIO Issues
- Verify pin numbering scheme (BCM vs BOARD)
- Check for conflicting pin usage
- Ensure proper voltage levels (3.3V logic)
- Use pull-up/pull-down resistors when needed

## Performance Optimization
- Use fast SD card (Class 10 or better)
- Enable GPU memory split for graphics applications
- Overclock CPU (with adequate cooling)
- Use USB 3.0 for external storage
- Monitor temperature: `vcgencmd measure_temp`

## Safety Guidelines
- Use proper 5V 3A power supply
- Avoid static electricity when handling
- Ensure adequate ventilation/cooling
- Don't exceed GPIO voltage limits (3.3V)
- Safely shutdown before removing power: `sudo shutdown -h now`
