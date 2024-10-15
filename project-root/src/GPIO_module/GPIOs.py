import RPi.GPIO as GPIO
import time
import os
import sys
import csv
from datetime import datetime


# Set up the GPIO pins
LED_PIN = 4
BUTTON_MAIN_PULL_PIN = 27  # GPIO pin for the main branch button
BUTTON_DEV_PULL_PIN = 22     # GPIO pin for the dev branch button
# Circuit setup:
# LED: GPIO 4 to resistor to LED Anode, LED Cathode to GND
# Button Main: GPIO 27 to button to GND
# Button Dev: GPIO 22 to button to GND

ULTRASONIC_TRIGGER_PIN = 23
ULTRASONIC_ECHO_PIN = 24

def setup_gpio():
    # Set up the GPIO pins
    GPIO.setmode(GPIO.BCM)
    # Set the LED pin as an output
    GPIO.setup(LED_PIN, GPIO.OUT)
    # The pin is pulled up, so the button will read LOW when pressed
    GPIO.setup(BUTTON_MAIN_PULL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_DEV_PULL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Set up the ultrasonic sensor pins
    GPIO.setup(ULTRASONIC_TRIGGER_PIN, GPIO.OUT)
    GPIO.setup(ULTRASONIC_ECHO_PIN, GPIO.IN)

def getDistanceFromSonic():
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
 
    return distance

def blink_led(times, interval):
        for _ in range(times):
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(interval)
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(interval)

def pull_from_git(branch):
    os.system(f'git pull origin {branch}')
    # Restart the script
    os.execv(sys.executable, ['python3'] + sys.argv)

def log_text(text, filePath):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filePath, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, text])

def syncGitOnButtonPush():
    # Path to the CSV file on the SD card
    filePath = "/home/administrator/projects/Remote_GPIO/repo/project-root/logs/dataLog.csv"

    try:
        print("Ready to pull from git...")
        while True:

            # Check for button presses
            if GPIO.input(BUTTON_MAIN_PULL_PIN) == GPIO.LOW:
                # Add a delay to check if both buttons are pressed, which leads to a shutdwon of the code
                time.sleep(0.5)
                if GPIO.input(BUTTON_DEV_PULL_PIN) == GPIO.LOW:
                    print("Shutting down...")
                # If only the main button is pressed, pull from the main branch
                print("Pulling from main branch...")
                log_text("          Pressed Button Main", filePath)
                pull_from_git('main')
                time.sleep(1)  # Debounce delay

            if GPIO.input(BUTTON_DEV_PULL_PIN) == GPIO.LOW:
                # Add a delay to check if both buttons are pressed, which leads to a shutdwon of the code
                time.sleep(0.5)
                if GPIO.input(BUTTON_MAIN_PULL_PIN) == GPIO.LOW:
                    print("Shutting down...")
                # If only the dev button is pressed, pull from the dev branch
                print("Pulling from dev branch...")
                log_text("Pressed Button Dev", filePath)
                pull_from_git('dev')
                time.sleep(1)  # Debounce delay

            
            distance = getDistanceFromSonic()
            print ("Gemessene Entfernung = %.1f mm" % distance)
            log_text("Distance: %.1f mm" % distance, filePath) 
            time.sleep(1)

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        GPIO.cleanup()