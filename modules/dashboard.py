from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

from modules.prices import get_price

console = Console()


def print_asset(name, symbol):

    price, change = get_price(symbol)

    if price is None:
        console.print(f"{name:<25} --", style="yellow")
        return

    arrow = "▲" if change >= 0 else "▼"
    color = "green" if change >= 0 else "red"

    console.print(
        f"{name:<25} {price:>10.2f}   [{color}]{arrow} {change:+.2f}%[/{color}]"
    )


def show_dashboard(config):

    console.print()

    console.print(
        Panel.fit(
            Text(
                "HORIAKTZ MARKET TERMINAL",
                justify="center",
                style="bold cyan",
            ),
            border_style="cyan",
        )
    )

    console.print(f"[green]● ONLINE[/green]    {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    console.print()

    console.rule("[bold cyan]INDEXES")

    print_asset("S&P 500", "^GSPC")
    print_asset("NASDAQ", "^IXIC")

    console.print()

    console.rule("[bold green]ETF")

    print_asset("VWCE", "VWCE.DE")
    print_asset("IUSN", "IUSN.DE")
    print_asset("VVSM", "VVSM.DE")

    console.print()

    console.rule("[bold yellow]BVB")

    console.print("Hidroelectrica            Coming Soon", style="yellow")
    console.print("OMV Petrom                Coming Soon", style="yellow")
    console.print("Banca Transilvania        Coming Soon", style="yellow")

    console.print()