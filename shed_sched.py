# Controls the relay connected to the heater in my shed
# If the temperature is below 20 degrees according to my BME280
# and it's between 8 and 5 on a weekday then turn the heater on

import RPi.GPIO as GPIO
import time
import smbus2
import bme280
from datetime import datetime
from pytz import timezone
import argparse

# Create the parser and add arguments
parser = argparse.ArgumentParser()

# Provide long form name as well (maps to 'argument3' not 'a3')
parser.add_argument('-t', '--target-temperature', type=int, default=20)
parser.add_argument('-g', '--gpio', type=int, default=12)
parser.add_argument('-st', '--start-time', type=int, default=8)
parser.add_argument('-et', '--end-time', type=int, default=17)
parser.add_argument('-tz', '--time-zone', type=str, default='Europe/London')

args = parser.parse_args()
target_temperature = args.target_temperature
gpio_number = args.gpio
start_time = args.start_time
end_time = args.end_time
time_zone = args.time_zone

print(f'Target Temperature is {target_temperature}C')
print(f'Using GPIO number {gpio_number}')
print(f'Starting at {start_time}:00 and ending at {end_time}:00')

GPIO.setwarnings(False)
mode = GPIO.getmode()
if mode != GPIO.BCM:
    GPIO.setmode(GPIO.BCM)  # GPIO Numbers instead of board numbers
    print("Setting GPIO Mode to BCM")

print(f'Running setup for GPIO {gpio_number}. Setting to OUT mode.')
RELAY_GPIO = gpio_number
GPIO.setup(RELAY_GPIO, GPIO.OUT)  # GPIO Assign mode


def get_temperature():
    port = 1
    address = 0x76
    bus = smbus2.SMBus(port)

    calibration_params = bme280.load_calibration_params(bus, address)

    # the sample method will take a single reading and return a
    # compensated_reading object
    data = bme280.sample(bus, address, calibration_params)

    # the compensated_reading class has the following attributes
    return round(data.temperature, 2)


def turn_on_relay():
    print("Turning on relay")
    GPIO.output(RELAY_GPIO, GPIO.HIGH)  # on


def turn_off_relay():
    print("Turning off relay")
    GPIO.output(RELAY_GPIO, GPIO.LOW)  # off


def is_working_hours():
    now = datetime.now(tz=timezone(time_zone))
    hour = now.hour
    day = now.weekday()
    if hour >= start_time and hour < end_time:
        print(f'Hour {hour} is within working hours')
        if day <= 4:  # 0 is Monday, 4 is Friday
            print(f'Day {day} is a working day')
            return True
        else:
            print(f'Day {day} is not a working day')
            return False
    else:
        print(f'Hour {hour} is not within working hours')
        return False


temperature = get_temperature()
print(f"The temperature in the shed is {temperature}")

if (temperature < target_temperature) and is_working_hours():
    turn_on_relay()
else:
    turn_off_relay()
