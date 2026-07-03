import os
import sys
from datetime import datetime

class Dashboard:
    def __init__(self):
        self.GREEN = '\033[38;5;82m'
        self.RED = '\033[38;5;196m'
        self.YELLOW = '\033[38;5;220m'
        self.BLUE = '\033[38;5;39m'
        self.CYAN = '\033[38;5;51m'
        self.MAGENTA = '\033[38;5;201m'
        self.WHITE = '\033[38;5;255m'
        self.GRAY = '\033[38;5;244m'
        self.BOLD = '\033[1m'
        self.RESET = '\033[0m'

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render(self, indices_data, movers_data, news_data, portfolio_data, currency_rates):
        self.clear_screen()
        t_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # HEADER TERMINAL
        print(f"{self.BOLD}{self.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{self.RESET}")
        print(f"{self.BOLD}{self.CYAN}║                      ⚡ HORIAKTZ MARKET TERMINAL v2.0 ⚡                     ║{self.RESET}")
        print(f"{self.BOLD}{self.CYAN}║  {self.GRAY}SYSTEM TIME: {t_now:<44} STATUS: ONLINE {self.CYAN}║{self.RESET}")
        print(f"{self.BOLD}{self.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{self.RESET}\n")

        # 1. INDICI
        print(f" {self.BOLD}{self.YELLOW}┌─── MARKET INDICES ─────────────────────────────────────────────────────────┐{self.RESET}")
        print(f" {self.BOLD}{self.WHITE}│ Ticker       │ Price      │ 1H         │ 1D         │ 1W         │ 1M         │{self.RESET}")
        print(f" {self.GRAY}├──────────────┼────────────┼────────────┼────────────┼────────────┼────────────┤{self.RESET}")
        for name, data in indices_data.items():
            c_1h = f"{self.GREEN}+{data['1H']}%" if data['1H'] >= 0 else f"{self.RED}{data['1H']}%"
            c_1d = f"{self.GREEN}+{data['1D']}%" if data['1D'] >= 0 else f"{self.RED}{data['1D']}%"
            c_1w = f"{self.GREEN}+{data['1W']}%" if data['1W'] >= 0 else f"{self.RED}{data['1W']}%"
            c_1m = f"{self.GREEN}+{data['1M']}%" if data['1M'] >= 0 else f"{self.RED}{data['1M']}%"
            print(f" │ {self.BOLD}{self.WHITE}{name:<12}{self.RESET} │ {data['price']:<10} │ {c_1h:<18}{self.RESET} │ {c_1d:<18}{self.RESET} │ {c_1w:<18}{self.RESET} │ {c_1m:<18}{self.RESET} │")
        print(f" {self.GRAY}└────────────────────────────────────────────────────────────────────────────┘{self.RESET}\n")

        # 2. MOVERS
        print(f" {self.BOLD}{self.YELLOW}┌─── TOP MARKET MOVERS ──────────────────────────────────────────────────────┐{self.RESET}")
        print(f" {self.BOLD}{self.WHITE}│ TOP GAINERS                          │ TOP LOSERS                          │{self.RESET}")
        print(f" {self.GRAY}├──────────────────────────────────────┼──────────────────────────────────────┤{self.RESET}")
        gainers = movers_data.get('gainers', [])
        losers = movers_data.get('losers', [])
        for i in range(max(len(gainers), len(losers))):
            g_str = "---"
            if i < len(gainers):
                g = gainers[i]
                g_str = f"{self.BOLD}{g['ticker']:<5}{self.RESET} {g['price']:>8} ({self.GREEN}+{g['change']}%{self.RESET})"
                g_str = f"{g_str:<{36 + len(self.GREEN) + len(self.RESET) + len(self.BOLD) + len(self.RESET)}}"
            else:
                g_str = f"{g_str:<36}"
            l_str = "---"
            if i < len(losers):
                l = losers[i]
                l_str = f"{self.BOLD}{l['ticker']:<5}{self.RESET} {l['price']:>8} ({self.RED}{l['change']}%{self.RESET})"
                l_str = f"{l_str:<{36 + len(self.RED) + len(self.RESET) + len(self.BOLD) + len(self.RESET)}}"
            else:
                l_str = f"{l_str:<36}"
            print(f" │ {g_str} │ {l_str} │")
        print(f" {self.GRAY}└────────────────────────────────────────────────────────────────────────────┘{self.RESET}\n")

        # 3. ȘTIRI
        print(f" {self.BOLD}{self.YELLOW}┌─── LATEST NEWS STREAM ─────────────────────────────────────────────────────┐{self.RESET}")
        for source, articles in news_data.items():
            source_color = self.MAGENTA if source == 'Bloomberg' else (self.BLUE if source == 'CNBC' else self.CYAN)
            print(f" │ {self.BOLD}{source_color}📡 {source.upper()}{self.RESET}")
            for art in articles:
                title = art['title'][:65] + "..." if len(art['title']) > 65 else art['title']
                print(f" │   {self.GRAY}[{art['time']}] {self.WHITE}{title:<68}{self.RESET} │")
            if source != list(news_data.keys())[-1]:
                print(f" {self.GRAY}├ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -┤{self.RESET}")
        print(f" {self.GRAY}└────────────────────────────────────────────────────────────────────────────┘{self.RESET}\n")

        # 4. PORTOFOLIU MIXT DE VALUTE
        print(f" {self.BOLD}{self.YELLOW}┌─── YOUR PORTFOLIO OVERVIEW ────────────────────────────────────────────────┐{self.RESET}")
        print(f" {self.BOLD}{self.WHITE}│ Asset    │ Qty    │ Price (Orig) │ Total Value  │ CCY │ P&L (Orig / %)             │{self.RESET}")
        print(f" {self.GRAY}├──────────┼────────┼──────────────┼──────────────┼─────┼────────────────────────────┤{self.RESET}")
        
        total_value_usd = 0
        total_pnl_usd = 0
        
        for row in portfolio_data:
            total_value_usd += row['value_usd']
            total_pnl_usd += row['pnl_usd']
            
            pnl_color = self.GREEN if row['pnl_val'] >= 0 else self.RED
            pnl_sign = "+" if row['pnl_val'] >= 0 else ""
            pnl_str = f"{pnl_color}{pnl_sign}{row['pnl_val']:,.2f} ({pnl_sign}{row['pnl_pct']}%){self.RESET}"
            
            print(f" │ {self.BOLD}{row['ticker']:<8}{self.RESET} │ {row['qty']:<6} │ {row['price']:<12.2f} │ {row['value']:<12,.2f} │ {row['currency']:<3} │ {pnl_str:<40} │")
            
        print(f" {self.GRAY}├──────────┴────────┴──────────────┴──────────────┴─────┴────────────────────────────┤{self.RESET}")
        
        # Conversie totaluri în fundal bazate pe USD
        usd_ron = currency_rates.get('USD_RON', 4.55)
        eur_ron = currency_rates.get('EUR_RON', 4.97)
        usd_eur = usd_ron / eur_ron
        
        total_value_ron = total_value_usd * usd_ron
        total_value_eur = total_value_usd * usd_eur
        
        total_pnl_ron = total_pnl_usd * usd_ron
        total_pnl_eur = total_pnl_usd * usd_eur
        
        tot_pnl_color = self.GREEN if total_pnl_usd >= 0 else self.RED
        tot_pnl_sign = "+" if total_pnl_usd >= 0 else ""
        cost_basis_usd = total_value_usd - total_pnl_usd
        pnl_pct = round((total_pnl_usd / cost_basis_usd) * 100, 2) if cost_basis_usd != 0 else 0.0
        
        val_summary = f"${total_value_usd:,.2f}  │  {total_value_ron:,.2f} RON  │  €{total_value_eur:,.2f}"
        pnl_summary = f"{tot_pnl_sign}${total_pnl_usd:,.2f}  │  {tot_pnl_sign}{total_pnl_ron:,.2f} RON  │  {tot_pnl_sign}€{total_pnl_eur:,.2f}  ({tot_pnl_sign}{pnl_pct}%)"
        
        print(f" │ {self.BOLD}{self.WHITE}TOTAL VALUE : {self.CYAN}{val_summary:<61}{self.RESET} │")
        print(f" │ {self.BOLD}{self.WHITE}TOTAL P&L   : {tot_pnl_color}{pnl_summary:<61}{self.RESET} │")
        print(f" {self.GRAY}└────────────────────────────────────────────────────────────────────────────┘{self.RESET}")