# Controls the relay connected to the heater in my shed
# If the temperature is below 20 degrees according to my BME280
# and it's between 8 and 5 on a weekday then turn the heater on

import RPi.GPIO as GPIO
import time
import smbus2
import bme280
from datetime import datetime
from pytz import timezone

target_temperature = 20
print(f"Target Temperature is {target_temperature}C")

GPIO.setwarnings(False)
mode = GPIO.getmode()
if mode != GPIO.BCM:
    GPIO.setmode(GPIO.BCM)  # GPIO Numbers instead of board numbers
    print("Setting GPIO Mode to BCM")

print("Running setup for GPIO 12. Setting to OUT mode.")
RELAY_1_GPIO = 12
GPIO.setup(RELAY_1_GPIO, GPIO.OUT)  # GPIO Assign mode


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
    GPIO.output(RELAY_1_GPIO, GPIO.HIGH)  # on


def turn_off_relay():
    print("Turning off relay")
    GPIO.output(RELAY_1_GPIO, GPIO.LOW)  # off


def is_working_hours():
    now = datetime.now(tz=timezone('Europe/London'))
    hour = now.hour
    day = now.weekday()
    if hour >= 8 and hour < 17:
        print(f'Hour {hour} is within working hours')
        if day <= 4:  # 0 is Monday, 4 is Friday
            print(f'Day {day} is a working day')
            return True
        else:
            print(f'Day {day} is not a working day')
            return True
    else:
        print(f'Hour {hour} is not within working hours')
        return False


temperature = get_temperature()
print(f"The temperature in the shed is {temperature}")

if (temperature < target_temperature) and is_working_hours():
    turn_on_relay()
else:
    turn_off_relay()
