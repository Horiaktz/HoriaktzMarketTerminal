import json
import os
from rich.console import Console
from rich.panel import Panel
from rich import box

from modules.dashboard import show_dashboard

console = Console()


def load_config():
    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    os.system("cls" if os.name == "nt" else "clear")

    console.print(
        Panel.fit(
            "[bold cyan]HORIAKTZ MARKET TERMINAL[/bold cyan]\n[green]Version 0.1[/green]",
            box=box.DOUBLE,
        )
    )

    show_dashboard(None)


if __name__ == "__main__":
    main()