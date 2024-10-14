from module import setup_gpio, syncGitOnButtonPush

def main():
    setup_gpio()
    syncGitOnButtonPush()

if __name__ == "__main__":
    main()