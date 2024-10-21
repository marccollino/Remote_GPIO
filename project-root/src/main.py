from GPIO_module.GPIOs import setup_gpio
from webserver_module import create_app

import RPi.GPIO as GPIO
import threading
import signal
import time
import sys
import os
from werkzeug.serving import make_server # Using `werkzeug.serving.make_server`:** This allows you to control the server more precisely, including shutting it down gracefully.

# A threading.Event named is created to signal when the server and GPIO setup should stop.
stop_event = threading.Event()

def main():
    try:
        setup_gpio()
        while not stop_event.is_set():
            time.sleep(1)
            pass
    except Exception as e:
        print(f"An error occurred: {e}")
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        GPIO.cleanup()
        print("Server and GPIO setup stopped.")
        
        # sys.exit(0)

# A signal_handler function is defined to handle SIGINT and SIGTERM signals, 
# which are typically sent when you press Ctrl+C or when the system is shutting down. 
# This function sets the stop event and exits the program.
def signal_handler(sig, frame):
    print("Signal received, stopping...")
    stop_event.set()
    sys.exit(0)

# handler for the shutdown request by the webserver
def shutdown_raspi():
    try:
        stop_event.set()
        # Add a delay to allow the server to respond to the request before shutting down.
        time.sleep(3)
        os.system('sudo shutdown -h now')
        return None
    except Exception as e:
        return f"An error occurred while shutting down: {e}"
    
# Handler for the restart request by the webserver
def restart_raspi():
    try:
        stop_event.set()
        time.sleep(3)
        os.system('sudo reboot')
        return None
    except Exception as e:
        return f"An error occurred while restarting: {e}"

if __name__ == "__main__":
    try:
        # The signal.signal function is used to register the signal_handler for SIGINT and SIGTERM signals.
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start the GPIO setup in a separate thread
        # --> This is done to prevent the webserver from blocking the GPIO setup
        gpio_thread = threading.Thread(target=main)
        gpio_thread.start()
    except Exception as e:
        print(f"An error occurred while setting up the GPIO: {e}")
        gpio_thread.join()
        stop_event.set()

    try:
        # create and run the webserver
        app = create_app()
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"An error occurred while setting up the server: {e}")
    finally:
        stop_event.set()
        gpio_thread.join()
        print("Server and GPIO setup stopped.")
