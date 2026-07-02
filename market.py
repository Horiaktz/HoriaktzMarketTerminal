import os
import sys
import time
from modules.dashboard import show_dashboard


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def main():

    while True:
        clear()
        show_dashboard(None)

        print("\n[R] Refresh   [Q] Quit   (Enter = refresh)")

        # citim input fără să blocheze tot UI-ul
        cmd = input("> ").strip().lower()

        if cmd == "q":
            clear()
            print("Closing Horiaktz Market Terminal...")
            time.sleep(0.5)
            sys.exit()

        # orice altceva = refresh
        continue


if __name__ == "__main__":
    main()