import time
import pigpio # The pigpio library is written in the C programming language.The pigpio daemon offers a socket and pipe interface to the underlying C library. A C library and a Python module allow control of the GPIO via the pigpio daemon.

# Set up the GPIO pins
ULTRASONIC_TRIGGER_PIN = 23
ULTRASONIC_ECHO_PIN = 24

duration = 0
startTime = 0
stopTime = 0

pi = None
callBack_1 = None
callBack_2 = None

# # Disable warnings regarding GPIO usage
# GPIO.setwarnings(False)

def rising_edge_callback(gpio, level, tick):
    global startTime
    startTime = tick

def falling_edge_callback(gpio, level, tick):
    global stopTime, duration, startTime
    stopTime = tick
    duration = stopTime - startTime

def setup_gpio():
    global pi, callBack_1, callBack_2
    # Initialize Pigpio
    pi = pigpio.pi()

    if not pi.connected:
        exit()

    # Set up the ultrasonic sensor pins
    pi.set_mode(ULTRASONIC_TRIGGER_PIN, pigpio.OUTPUT)
    pi.set_mode(ULTRASONIC_ECHO_PIN, pigpio.INPUT)
    callBack_1 = pi.callback(ULTRASONIC_ECHO_PIN, pigpio.RISING_EDGE, rising_edge_callback)
    callBack_2 = pi.callback(ULTRASONIC_ECHO_PIN, pigpio.FALLING_EDGE, falling_edge_callback)

def cleanup_gpio():
    global pi, callBack_1, callBack_2
    callBack_1.cancel()
    callBack_2.cancel()
    pi.stop()

def getDistanceFromSonic(sonicVelocity):
    global duration
    global edgecount
    duration = 0
    distance = 0
    try:
        # Set trigger to False (Low)
        pi.write(ULTRASONIC_TRIGGER_PIN, 0)
        time.sleep(0.01)
        returnPackage = {'duration': 9999, 'distance': 9999, 'error': None}

        # setze Trigger auf HIGH
        pi.write(ULTRASONIC_TRIGGER_PIN, 1)
        # setze Trigger nach 0.01ms aus LOW
        time.sleep(0.00001)
        pi.write(ULTRASONIC_TRIGGER_PIN, 0)
    
        # Wait for the echo to be received
        while duration == 0:
            time.sleep(0.01)  # Sleep for 1ms to prevent busy waiting

        returnPackage['duration'] =  duration # microseconds

        # Convert the duration to seconds
        duration = duration / 1000000  # seconds
    
        # mit der Schallgeschwindigkeit (343200 mm/s) multiplizieren
        # und durch 2 teilen, da hin und zurueck
        distance = (duration * sonicVelocity) / 2
        #Round the distance to 2 decimal places
        distance = round(distance, 2)
        returnPackage['distance'] = distance        

    except Exception as e:
        returnPackage['error'] = f"An error occurred: {e}"
        cleanup_gpio()
        
    return returnPackage