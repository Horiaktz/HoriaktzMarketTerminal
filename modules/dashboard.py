from datetime import datetime

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

from modules.prices import get_price
from modules.portfolio import get_portfolio, get_bvb
from modules.news import get_news

console = Console()


INDICES = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW JONES": "^DJI",
}


# ---------------- DASHBOARD ----------------
def build_dashboard():

    layout = Layout()

    # 🔥 WIDE LAYOUT (mai aerisit)
    layout.split_column(
        Layout(name="header", size=4),
        Layout(name="body"),
        Layout(name="footer", size=7),
    )

    layout["body"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="center", ratio=2),
        Layout(name="right", ratio=1),
    )

    # ---------------- HEADER ----------------
    layout["header"].update(
        Panel(
            f"[bold cyan]HORIAKTZ MARKET TERMINAL[/bold cyan]\n"
            f"[green]CLEAN TRADER v1.3[/green]\n"
            f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
            border_style="cyan",
        )
    )

    # ---------------- INDICES ----------------
    t = Table(title="INDICES", expand=True)

    t.add_column("Index")
    t.add_column("Price")
    t.add_column("Change")

    for name, sym in INDICES.items():

        price, change = get_price(sym)

        if price is None:
            continue

        color = "green" if change >= 0 else "red"

        t.add_row(
            name,
            f"{price:.2f}",
            f"[{color}]{change:+.2f}%[/{color}]"
        )

    layout["body"]["left"].update(t)

    # ---------------- PORTFOLIO ----------------
    portfolio = get_portfolio()

    p = Table(title="PORTFOLIO", expand=True)

    p.add_column("Asset")
    p.add_column("Qty")
    p.add_column("Price")
    p.add_column("Value")
    p.add_column("P&L %")

    total_value = 0
    total_cost = 0

    for symbol, data in portfolio.items():

        qty = data["qty"]
        avg = data["avg_price"]

        price, change = get_price(symbol)

        if price is None:
            continue

        value = price * qty
        cost = avg * qty

        pnl_pct = ((value - cost) / cost) * 100 if cost else 0

        total_value += value
        total_cost += cost

        color = "green" if pnl_pct >= 0 else "red"

        p.add_row(
            symbol,
            str(qty),
            f"{price:.2f}",
            f"{value:.2f}",
            f"[{color}]{pnl_pct:+.2f}%[/{color}]"
        )

    p.caption = f"TOTAL VALUE: {total_value:.2f}"

    layout["body"]["center"].update(p)

    # ---------------- BVB (MANUAL) ----------------
    bvb = get_bvb()

    b = Table(title="BVB HOLDINGS", expand=True)

    b.add_column("Stock")
    b.add_column("Qty")

    for name, qty in bvb.items():
        b.add_row(name, str(qty))

    layout["body"]["right"].update(b)

    # ---------------- NEWS (10 + SOURCES) ----------------
    try:
        news = get_news()
    except:
        news = []

    news_text = "[bold magenta]NEWS FEED[/bold magenta]\n\n"

    for i, n in enumerate(news[:10], 1):
        news_text += f"{i}. {n}\n"
        news_text += "   source: Yahoo Finance / MarketWatch / Reuters\n\n"

    # ---------------- FOOTER (CLEAR HOTKEYS) ----------------
    footer = (
        news_text +
        "\n" +
        "────────────────────────────────────────────\n" +
        "[bold green][R][/bold green] Refresh script   |   [bold red][Q][/bold red] Quit terminal\n"
    )

    layout["footer"].update(
        Panel(footer, border_style="magenta")
    )

    return layout


def show_dashboard(_):
    console.print(build_dashboard())