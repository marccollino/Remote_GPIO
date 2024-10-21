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

# duration = 0
# startTime = 0
# stopTime = 0

# # Disable warnings regarding GPIO usage
# GPIO.setwarnings(False)

def setup_gpio():
    # Set up the GPIO pins
    GPIO.setmode(GPIO.BCM)
    
    # Set up the ultrasonic sensor pins
    GPIO.setup(ULTRASONIC_TRIGGER_PIN, GPIO.OUT)
    GPIO.setup(ULTRASONIC_ECHO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # # Add event detection for rising and falling edges
    # GPIO.add_event_detect(ULTRASONIC_ECHO_PIN, GPIO.RISING, callback=rising_edge_callback)
    # GPIO.add_event_detect(ULTRASONIC_ECHO_PIN, GPIO.FALLING, callback=falling_edge_callback)

# def getDistanceFromSonic_high_priority():
#     # Create a queue to get the result from the thread
#     result_queue = queue.Queue()
#     # Create and start the thread
#     thread = threading.Thread(target=run_getDistanceFromSonic, args=(result_queue,))
#     thread.start()
#     thread.join()

#     returnPackage = result_queue.get()

#     # Return the result from the thread
#     return returnPackage

# def run_getDistanceFromSonic(result_queue):
#     # Set the thread to a higher priority using psutil
#     os.nice(0)  # -20 is the highest priority. 19 is the lowest priority.

#     # Run the function
#     returnPackage = getDistanceFromSonic()

#     # Put the result in the queue
#     result_queue.put(returnPackage)

#     return returnPackage

# def rising_edge_callback(channel):
#     global startTime
#     startTime = time.perf_counter()
#     print("Rising edge detected at ", startTime)

# def falling_edge_callback(channel):
#     global startTime, stopTime, duration
#     stoptime = time.perf_counter()
#     duration = stoptime - startTime
#     print("Falling edge detected at ", stoptime)

def getDistanceFromSonic():
    # global duration
    try:
        returnPackage = {'data': 9999, 'error': None}

        # # Set trigger to False (Low)
        # GPIO.output(ULTRASONIC_TRIGGER_PIN, False)
        # time.sleep(0.1)

        startTime = time.perf_counter()
        stopTime = time.perf_counter()

        # setze Trigger auf HIGH
        GPIO.output(ULTRASONIC_TRIGGER_PIN, True)
        # setze Trigger nach 0.01ms aus LOW
        time.sleep(0.00001)
        GPIO.output(ULTRASONIC_TRIGGER_PIN, False)
    
        # # Wait for the echo to be received
        # while duration == 0:
        #     time.sleep(0.001)  # Sleep for 1ms to prevent busy waiting
        # print("Duration: ", duration)

        while GPIO.input(ULTRASONIC_ECHO_PIN) == 0:
            startTime = time.perf_counter()

        while GPIO.input(ULTRASONIC_ECHO_PIN) == 1:
            stopTime = time.perf_counter()

        duration = stopTime - startTime
    
        # mit der Schallgeschwindigkeit (343200 mm/s) multiplizieren
        # und durch 2 teilen, da hin und zurueck
        distance = (duration * (ultraSonicVelocity_0C + (temperatureEnvironment * ultraSonicVelocity_increase_1C))) / 2
        returnPackage['data'] = distance

    except Exception as e:
        returnPackage['error'] = f"An error occurred: {e}"
        GPIO.cleanup()
        
    return returnPackage