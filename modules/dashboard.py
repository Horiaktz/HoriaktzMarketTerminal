from datetime import datetime
from rich.console import Console
from rich.panel import Panel

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


def show_dashboard(_):

    console.print()

    # HEADER
    console.print(
        Panel.fit(
            "[bold cyan]HORIAKTZ MARKET TERMINAL[/bold cyan]\n"
            "[green]v0.2[/green]",
            border_style="cyan",
        )
    )

    console.print(
        f"[green]● ONLINE[/green]  {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
    )

    console.print()

    # INDEXES
    console.rule("[bold cyan]INDEXES")

    print_asset("S&P 500", "^GSPC")
    print_asset("NASDAQ", "^IXIC")

    console.print()

    # ETF
    console.rule("[bold green]ETF")

    print_asset("VWCE", "VWCE.DE")
    print_asset("IUSN", "IUSN.DE")
    print_asset("VVSM", "VVSM.DE")

    console.print()

    # BVB (temporar fără erori)
    console.rule("[bold yellow]BVB")

    print_asset("Hidroelectrica", "H2O.BX")
    print_asset("OMV Petrom", "SNP.BX")
    print_asset("Banca Transilvania", "TLV.BX")

    console.print()

    console.rule("[bold white]READY")