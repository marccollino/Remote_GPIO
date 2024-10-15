from GPIO_module.GPIOs import setup_gpio, syncGitOnButtonPush

def main():
    try:
        setup_gpio()
        syncGitOnButtonPush()
    except Exception as e:
        print("An error occurred: " + str(e))
    except KeyboardInterrupt:
        print("Exiting program")

if __name__ == "__main__":
    main()