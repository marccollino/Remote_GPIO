import RPi.GPIO as GPIO
import time
import threading
import os
import queue
import psutil

# Set up the GPIO pins
ULTRASONIC_TRIGGER_PIN = 23
ULTRASONIC_ECHO_PIN = 24

temperatureEnvironment = 24 # Celsius
ultraSonicVelocity_0C = 331300 # mm/s
ultraSonicVelocity_increase_1C = 600 # mm/s

duration = 0
startTime = 0
stopTime = 0
edgecount = 0

# # Disable warnings regarding GPIO usage
# GPIO.setwarnings(False)

def edge_detected_callback(channel):
    timeBuffer = time.perf_counter()
    global startTime, stopTime, edgecount, duration 
    if edgecount == 0:
        startTime = timeBuffer
        edgecount += 1
    elif edgecount == 1:
        stopTime = timeBuffer
        duration = stopTime - startTime

def setup_gpio():
    # Set up the GPIO pins
    GPIO.setmode(GPIO.BCM)

    # Set up the ultrasonic sensor pins
    GPIO.setup(ULTRASONIC_TRIGGER_PIN, GPIO.OUT)
    GPIO.setup(ULTRASONIC_ECHO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(ULTRASONIC_ECHO_PIN, GPIO.BOTH, callback=edge_detected_callback)

def cleanup_gpio():
    GPIO.cleanup()

def getDistanceFromSonic():
    global duration
    global edgecount
    try:
        # Set trigger to False (Low)
        GPIO.output(ULTRASONIC_TRIGGER_PIN, False)
        time.sleep(0.1)
        returnPackage = {'duration': 9999, 'distance': 9999, 'error': None}

        # setze Trigger auf HIGH
        GPIO.output(ULTRASONIC_TRIGGER_PIN, True)
        # setze Trigger nach 0.01ms aus LOW
        time.sleep(0.00001)
        GPIO.output(ULTRASONIC_TRIGGER_PIN, False)
    
        # Wait for the echo to be received
        while duration == 0:
            time.sleep(0.00001)  # Sleep for 1ms to prevent busy waiting

        #Round the duration to 6 decimal places
        duration = round(duration, 6)
        returnPackage['duration'] = duration
        edgecount = 0
    
        # mit der Schallgeschwindigkeit (343200 mm/s) multiplizieren
        # und durch 2 teilen, da hin und zurueck
        distance = (duration * (ultraSonicVelocity_0C + (temperatureEnvironment * ultraSonicVelocity_increase_1C))) / 2
        #Round the distance to 2 decimal places
        distance = round(distance, 2)
        returnPackage['distance'] = distance

    except Exception as e:
        returnPackage['error'] = f"An error occurred: {e}"
        cleanup_gpio()
        
    return returnPackage