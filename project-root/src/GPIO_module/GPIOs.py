import time
import pigpio # The pigpio library is written in the C programming language.The pigpio daemon offers a socket and pipe interface to the underlying C library. A C library and a Python module allow control of the GPIO via the pigpio daemon.

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

pi = None
cb = None

# # Disable warnings regarding GPIO usage
# GPIO.setwarnings(False)

def edge_detected_callback(gpio, level, tick):
    global startTime, stopTime, edgecount, duration 

    if edgecount == 0:
        startTime = tick # microseconds
        edgecount += 1
    elif edgecount == 1:
        stopTime = tick
        duration = stopTime - startTime
        edgecount = 0  # Reset edgecount for the next measurement

def setup_gpio():
    global pi, cb
    # Initialize Pigpio
    pi = pigpio.pi()

    if not pi.connected:
        exit()

    # Set up the ultrasonic sensor pins
    pi.set_mode(ULTRASONIC_TRIGGER_PIN, pigpio.OUTPUT)
    pi.set_mode(ULTRASONIC_ECHO_PIN, pigpio.INPUT)
    cb = pi.callback(ULTRASONIC_ECHO_PIN, pigpio.EITHER_EDGE, edge_detected_callback)

def cleanup_gpio():
    global pi, cb
    cb.cancel()
    pi.stop()

def getDistanceFromSonic():
    global duration
    global edgecount
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
        edgecount = 0
    
        # mit der Schallgeschwindigkeit (343200 mm/s) multiplizieren
        # und durch 2 teilen, da hin und zurueck
        distance = (duration * (ultraSonicVelocity_0C + (temperatureEnvironment * ultraSonicVelocity_increase_1C))) / 2
        #Round the distance to 2 decimal places
        distance = round(distance, 2)
        returnPackage['distance'] = distance
        duration = 0
        distance = 0

        print(returnPackage)

    except Exception as e:
        returnPackage['error'] = f"An error occurred: {e}"
        cleanup_gpio()
        
    return returnPackage