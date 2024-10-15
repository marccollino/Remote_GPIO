from GPIO_module.GPIOs import setup_gpio
from webserver_module import create_app

import RPi.GPIO as GPIO

import threading
import signal
import sys

# A threading.Event named is created to signal when the server and GPIO setup should stop.
stop_event = threading.Event()

def main():
    try:
        setup_gpio()
        #  loop to keep running until the stop event is set
        while not stop_event.is_set():
            # Your GPIO code here
            pass
    except Exception as e:
        print("An error occurred: " + str(e))
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        GPIO.cleanup()

# A signal_handler function is defined to handle SIGINT and SIGTERM signals, 
# which are typically sent when you press Ctrl+C or when the system is shutting down. 
# This function sets the stop event and exits the program.
def signal_handler(sig, frame):
    print("Signal received, stopping...")
    stop_event.set()
    sys.exit(0)

if __name__ == "__main__":
    # The signal.signal function is used to register the signal_handler for SIGINT and SIGTERM signals.
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start the GPIO setup in a separate thread
    # --> This is done to prevent the webserver from blocking the GPIO setup
    gpio_thread = threading.Thread(target=main)
    gpio_thread.start()

    # create and run the webserver
    app = create_app()
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        stop_event.set()
        gpio_thread.join()
        print("Server and GPIO setup stopped.")
