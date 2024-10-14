from GPIO_module.GPIOs import setup_gpio, syncGitOnButtonPush

def main():
    setup_gpio()
    syncGitOnButtonPush()

if __name__ == "__main__":
    main()