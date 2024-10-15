import RPi.GPIO as GPIO
import time

# Set up the GPIO pins
ULTRASONIC_TRIGGER_PIN = 23
ULTRASONIC_ECHO_PIN = 24

def setup_gpio():
    # Set up the GPIO pins
    GPIO.setmode(GPIO.BCM)
    
    # Set up the ultrasonic sensor pins
    GPIO.setup(ULTRASONIC_TRIGGER_PIN, GPIO.OUT)
    GPIO.setup(ULTRASONIC_ECHO_PIN, GPIO.IN)

def getDistanceFromSonic():
    try:
        returnPackage = {'data': 9999, 'error':''}

        # setze Trigger auf HIGH
        GPIO.output(ULTRASONIC_TRIGGER_PIN, True)
    
        # setze Trigger nach 0.01ms aus LOW
        time.sleep(0.00001)
        GPIO.output(ULTRASONIC_TRIGGER_PIN, False)
    
        startTime = time.time()
        stopTime = time.time()
    
        # speichere Startzeit
        while GPIO.input(ULTRASONIC_ECHO_PIN) == 0:
            startTime = time.time()
    
        # speichere Ankunftszeit
        while GPIO.input(ULTRASONIC_ECHO_PIN) == 1:
            stopTime = time.time()
    
        # Zeit Differenz zwischen Start und Ankunft
        TimeElapsed = stopTime - startTime
        # mit der Schallgeschwindigkeit (343000 mm/s) multiplizieren
        # und durch 2 teilen, da hin und zurueck
        distance = (TimeElapsed * 343000) / 2
        returnPackage['data'] = distance

    except Exception as e:
        GPIO.cleanup()
        returnPackage['error'] = f"An error occurred: {e}"
        
    return returnPackage