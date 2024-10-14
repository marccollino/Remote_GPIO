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

def setup_gpio():
    # Set up the GPIO pins
    GPIO.setmode(GPIO.BCM)
    # Set the LED pin as an output
    GPIO.setup(LED_PIN, GPIO.OUT)
    # The pin is pulled up, so the button will read LOW when pressed
    GPIO.setup(BUTTON_MAIN_PULL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_DEV_PULL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def syncGitOnButtonPush():
    # Path to the CSV file on the SD card
    csv_file_path = "/home/administrator/projects/Remote_GPIO/repo/project-root/logs/dataLog.csv"

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

    def log_button_press(button_name):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, button_name])
        print(f"Logged {button_name} press at {timestamp}")

    try:
        # Blink the LED 5 times at the start
        blink_led(5, 0.5)
        print("Ready to pull from git...")

        while True:
            # Check for button presses

            if GPIO.input(BUTTON_MAIN_PULL_PIN) == GPIO.LOW:
                # Add a delay to check if both buttons are pressed, which leads to a shutdwon of the code
                time.sleep(0.5)
                if GPIO.input(BUTTON_DEV_PULL_PIN) == GPIO.LOW:
                    print("Shutting down...")
                    blink_led(1, 5)
                    break
                # If only the main button is pressed, pull from the main branch
                print("Pulling from main branch...")
                log_button_press("Main")
                pull_from_git('main')
                time.sleep(1)  # Debounce delay
                # Short blink to indicate the pull is complete
                blink_led(2, 0.2)

            if GPIO.input(BUTTON_DEV_PULL_PIN) == GPIO.LOW:
                # Add a delay to check if both buttons are pressed, which leads to a shutdwon of the code
                time.sleep(0.5)
                if GPIO.input(BUTTON_MAIN_PULL_PIN) == GPIO.LOW:
                    print("Shutting down...")
                    blink_led(1, 5)
                    break
                # If only the dev button is pressed, pull from the dev branch
                print("Pulling from dev branch...")
                log_button_press("Dev")
                pull_from_git('dev')
                time.sleep(1)  # Debounce delay
                blink_led(2, 0.2)

            time.sleep(0.1)  # Small delay to avoid high CPU usage

    except Exception as e:
        print(f"An error occurred: {e}")
        blink_led(10, 0.1)
    except KeyboardInterrupt:
        # Error handling: blink the LED 4 times slowly
        blink_led(10, 0.1)
        pass
    finally:
        GPIO.cleanup()