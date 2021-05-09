#!/usr/bin/env python
# Controls the relay connected to the heater in my shed.

import RPi.GPIO as GPIO
import time
import smbus2
import bme280
from datetime import datetime
from pytz import timezone
import argparse
import time
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

# Create the parser and add arguments
parser = argparse.ArgumentParser()

parser.add_argument('-t', '--target-temperature', type=float, default=20.0)
parser.add_argument('-g', '--gpio', type=int, default=12)
parser.add_argument('-st', '--start-time', type=int, default=8)
parser.add_argument('-et', '--end-time', type=int, default=17)
parser.add_argument('-ed', '--end-day', type=int, default=4)
parser.add_argument('-tz', '--time-zone', type=str, default='Europe/London')
parser.add_argument('-d', '--delay', type=int, default=300)
parser.add_argument('-l', '--loop', type=int, default=10)

args = parser.parse_args()
TARGET_TEMPERATURE = args.target_temperature
RELAY_GPIO = args.gpio
START_TIME = args.start_time
END_TIME = args.end_time
END_DAY = args.end_day
TIME_ZONE = args.time_zone
DELAY = args.delay
LOOP = args.loop

logging.info(f'Target Temperature is {TARGET_TEMPERATURE}°C')
logging.info(f'Using GPIO number {RELAY_GPIO}')
logging.info(f'Starting at {START_TIME}:00 and ending at {END_TIME}:00')

GPIO.setwarnings(False)
mode = GPIO.getmode()
if mode != GPIO.BCM:
    GPIO.setmode(GPIO.BCM)  # GPIO Numbers instead of board numbers
    logging.info("Setting GPIO Mode to BCM")

logging.info(
    f'Running setup for GPIO {RELAY_GPIO}. Setting to OUT mode and ensuring turned off.')
GPIO.setup(RELAY_GPIO, GPIO.OUT)  # GPIO Assign mode
GPIO.output(RELAY_GPIO, GPIO.LOW)  # off


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
    logging.info("Turning on relay")
    GPIO.output(RELAY_GPIO, GPIO.HIGH)  # on


def turn_off_relay():
    logging.info("Turning off relay")
    GPIO.output(RELAY_GPIO, GPIO.LOW)  # off


def is_working_hours():
    now = datetime.now(tz=timezone(TIME_ZONE))
    hour = now.hour
    day = now.weekday()
    if hour >= START_TIME and hour < END_TIME:
        logging.info(f'Hour {hour} is within working hours')
        if day <= END_DAY:  # 0 is Monday, 4 is Friday
            logging.info(f'Day {day} is a working day')
            return True
        else:
            logging.info(f'Day {day} is not a working day')
            return False
    else:
        logging.info(f'Hour {hour} is not within working hours')
        return False


last_turned_off = None
last_state = False

while True:
    temperature = get_temperature()
    logging.info(f'The temperature in the shed is {temperature}°C')

    now = datetime.now()

    if last_turned_off:
        seconds_diff = round((now - last_turned_off).total_seconds())
        logging.info(f'Heater was last turned off {seconds_diff} seconds ago')

    if (temperature < TARGET_TEMPERATURE) and is_working_hours():
        if not last_state and (not last_turned_off or seconds_diff > DELAY):
            turn_on_relay()
            last_state = True
    elif last_state:
        turn_off_relay()
        last_turned_off = now
        last_state = False
    time.sleep(LOOP)
