import time
import sys
import threading
from modules.indices import IndicesManager
from modules.movers import MoversManager
from modules.news import NewsManager
from modules.portfolio import PortfolioManager
from modules.dashboard import Dashboard
from modules.charts import ChartManager
from modules.utils import CurrencyConverter

data_lock = threading.Lock()
indices_data = {}
movers_data = {}
news_data = {}
portfolio_data = []
currency_rates = {'USD_RON': 4.57, 'EUR_RON': 5.23}
running = True

def data_fetcher_loop(indices_mgr, movers_mgr, news_mgr, portfolio_mgr, converter, dashboard):
    global indices_data, movers_data, news_data, portfolio_data, currency_rates, running
    
    while running:
        try:
            i_data = indices_mgr.get_indices_data()
            m_data = movers_mgr.get_market_movers()
            n_data = news_mgr.get_latest_news()
            p_data = portfolio_mgr.get_portfolio_data()
            rates = converter.get_rates()
            
            with data_lock:
                indices_data = i_data
                movers_data = m_data
                news_data = n_data
                portfolio_data = p_data
                currency_rates = rates
            
            trigger_render(dashboard)
            
        except Exception:
            pass
        
        for _ in range(60):
            if not running:
                break
            time.sleep(1)

def trigger_render(dashboard):
    with data_lock:
        if indices_data:
            dashboard.render(indices_data, movers_data, news_data, portfolio_data, currency_rates)
            print(f"\n {dashboard.BOLD}{dashboard.YELLOW}[ COMMANDS ]{dashboard.RESET}  "
                  f"{dashboard.CYAN}q{dashboard.RESET} = Quit | "
                  f"{dashboard.CYAN}r{dashboard.RESET} = Force Refresh | "
                  f"{dashboard.CYAN}g{dashboard.RESET} = Charts | "
                  f"{dashboard.CYAN}p{dashboard.RESET} = Manage Portfolio")
            print(f"{dashboard.BOLD}{dashboard.CYAN}================================================================================{dashboard.RESET}")
            sys.stdout.write(f"\n {dashboard.BOLD}Action:{dashboard.RESET} ")
            sys.stdout.flush()

def main():
    global running, indices_data, movers_data, news_data, portfolio_data, currency_rates
    
    indices_mgr = IndicesManager()
    movers_mgr = MoversManager()
    news_mgr = NewsManager()
    portfolio_mgr = PortfolioManager()
    converter = CurrencyConverter()
    dashboard = Dashboard()
    chart_mgr = ChartManager()

    dashboard.clear_screen()
    print("Se inițializează terminalul interactiv Horiaktz v2.0...")
    # Restaurat textul detaliat de pornire original:
    print("Descărcăm primele date din piață (poate dura câteva secunde)...")

    fetcher_thread = threading.Thread(
        target=data_fetcher_loop, 
        args=(indices_mgr, movers_mgr, news_mgr, portfolio_mgr, converter, dashboard),
        daemon=True
    )
    fetcher_thread.start()

    while running:
        try:
            cmd = input().strip().lower()
            if cmd == 'q':
                running = False
                # Restaurat mesajul de închidere cu urare:
                print(f"\n{dashboard.GREEN}Terminal oprit cu succes. O zi profitabilă!{dashboard.RESET}")
                sys.exit(0)
            elif cmd == 'r':
                dashboard.clear_screen()
                print(f"{dashboard.YELLOW}Se forțează împrospătarea datelor...{dashboard.RESET}")
                indices_data = indices_mgr.get_indices_data()
                movers_data = movers_mgr.get_market_movers()
                news_data = news_mgr.get_latest_news()
                portfolio_data = portfolio_mgr.get_portfolio_data()
                currency_rates = converter.get_rates()
                trigger_render(dashboard)
            elif cmd == 'g':
                # Restaurat indiciul cu exemple de tickere:
                sys.stdout.write(f"\n Introdu tickerele separate prin virgulă (ex: AAPL, TSLA, BTC-USD): ")
                sys.stdout.flush()
                tickers_input = input().strip()
                if tickers_input:
                    tickers_list = [t.strip() for t in tickers_input.split(',') if t.strip()]
                    dashboard.clear_screen()
                    print(f"{dashboard.YELLOW}Se descarcă datele pentru activele solicitate...{dashboard.RESET}\n")
                    for ticker in tickers_list:
                        print(chart_mgr.draw_ascii_chart(ticker, days=25))
                print(f"\n{dashboard.CYAN}Apasă ENTER pentru a te întoarce la dashboard...{dashboard.RESET}")
                input()
                trigger_render(dashboard)
            elif cmd == 'p':
                dashboard.clear_screen()
                print("Meniu Portofoliu activat.")
                portfolio_data = portfolio_mgr.get_portfolio_data()
                trigger_render(dashboard)
            else:
                trigger_render(dashboard)
        except (KeyboardInterrupt, EOFError):
            running = False
            sys.exit(0)

if __name__ == "__main__":
    main()