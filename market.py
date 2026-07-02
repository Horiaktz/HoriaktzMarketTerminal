import os
from modules.dashboard import show_dashboard


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def main():
    while True:
        clear()
        show_dashboard(None)

        cmd = input("> ").strip().lower()

        if cmd == "q":
            break


if __name__ == "__main__":
    main()