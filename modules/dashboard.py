from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout

from modules.prices import get_price
from modules.news import get_news

console = Console()


def asset_line(name, symbol):
    price, change = get_price(symbol)

    if price is None:
        return f"{name:<15} --"

    arrow = "▲" if change >= 0 else "▼"
    return f"{name:<15} {price:>10.2f} {arrow} {change:+.2f}%"


def build_dashboard():

    layout = Layout()

    layout.split_column(
        Layout(name="header", size=5),
        Layout(name="body"),
        Layout(name="footer", size=3),
    )

    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right"),
    )

    # HEADER
    layout["header"].update(
        Panel.fit(
            f"[bold cyan]HORIAKTZ MARKET TERMINAL[/bold cyan]\n"
            f"[green]v0.4[/green]   [white]{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}[/white]",
            border_style="cyan",
        )
    )

    # LEFT (MARKET)
    left = "\n".join([
        "[bold cyan]MARKET[/bold cyan]",
        "",
        asset_line("S&P500", "^GSPC"),
        asset_line("NASDAQ", "^IXIC"),
        "",
        "[bold green]ETF[/bold green]",
        "",
        asset_line("VWCE", "VWCE.DE"),
        asset_line("IUSN", "IUSN.DE"),
        asset_line("VVSM", "VVSM.DE"),
        "",
        "[bold yellow]BVB[/bold yellow]",
        "",
        "Hidroelectrica   --",
        "OMV Petrom       --",
        "Banca Transilvania --",
    ])

    layout["body"]["left"].update(
        Panel(left, title="Markets", border_style="cyan")
    )

    # RIGHT (NEWS)
    try:
        news_items = get_news()
    except:
        news_items = []

    news_text = "[bold magenta]NEWS[/bold magenta]\n\n"

    if news_items:
        for n in news_items[:6]:
            news_text += f"• {n}\n"
    else:
        news_text += "No news available"

    layout["body"]["right"].update(
        Panel(news_text, title="Market News", border_style="magenta")
    )

    # FOOTER
    layout["footer"].update(
        Panel(
            "[R] Refresh   [Q] Quit",
            border_style="white",
        )
    )

    return layout


def show_dashboard(_):
    console.print(build_dashboard())