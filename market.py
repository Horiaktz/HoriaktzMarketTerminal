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
                sys.stdout.write(f"\n Introdu tickerele separate prin virgulă (ex: AAPL, TSLA, BTC-USD): ")
                sys.stdout.flush()
                tickers_input = input().strip()
                if tickers_input:
                    tickers_list = [t.strip().upper() if '.' in t else (f"{t.strip().upper()}.DE" if t.strip().lower() in ['vwce', 'iusn', 'vvsm'] else t.strip().upper()) for t in tickers_input.split(',') if t.strip()]
                    dashboard.clear_screen()
                    print(f"{dashboard.YELLOW}Se descarcă datele pentru activele solicitate...{dashboard.RESET}\n")
                    for ticker in tickers_list:
                        print(chart_mgr.draw_ascii_chart(ticker, days=25))
                print(f"\n{dashboard.CYAN}Apasă ENTER pentru a te întoarce la dashboard...{dashboard.RESET}")
                input()
                refresh_and_render(indices_mgr, movers_mgr, news_mgr, portfolio_mgr, converter, dashboard)
            elif cmd == 'p':
                in_p_menu = True
                while in_p_menu:
                    dashboard.clear_screen()
                    print(f"{dashboard.BOLD}{dashboard.YELLOW}══💼 MENIU MANAGE PORTFOLIO ════════════════════════════════════════════════════{dashboard.RESET}")
                    print(f" 1. {dashboard.CYAN}Vizualizează Alocarea Activelor{dashboard.RESET} (Grafic ASCII pe ponderi)")
                    print(f" 2. {dashboard.CYAN}Adaugă Activ Nou{dashboard.RESET} (XTB sau Tradeville/BVB)")
                    print(f" 3. {dashboard.CYAN}Modifică / Actualizează Complet un Activ{dashboard.RESET}")
                    print(f" 4. {dashboard.YELLOW}Actualizează Rapid Prețuri BVB (Manual){dashboard.RESET}")
                    print(f" 5. {dashboard.RED}Șterge un Activ{dashboard.RESET}")
                    print(f" 6. {dashboard.GREEN}Înapoi la Dashboard{dashboard.RESET}")
                    print(f"{dashboard.BOLD}{dashboard.YELLOW}════════════════════════════════════════════════════════════════════════════════{dashboard.RESET}")
                    sys.stdout.write(f"\n Selectează o opțiune (1-6): ")
                    sys.stdout.flush()
                    
                    p_opt = input().strip()
                    if p_opt == '1':
                        dashboard.clear_screen()
                        print(f"{dashboard.BOLD}{dashboard.YELLOW}══📈 ALOCARE PORTOFOLIU ════════════════════════════════════════════════════════{dashboard.RESET}")
                        with data_lock:
                            current_p_data = list(portfolio_data)
                        print(portfolio_mgr.generate_allocation_chart(current_p_data))
                        print(f"\n{dashboard.CYAN}Apasă ENTER pentru a reveni la meniu...{dashboard.RESET}")
                        input()
                    elif p_opt == '2':
                        dashboard.clear_screen()
                        print(f"{dashboard.BOLD}{dashboard.YELLOW}══➕ ADĂUGARE ACTIV ════════════════════════════════════════════════════════════{dashboard.RESET}")
                        ticker = input(" Introdu Ticker (ex: SNP, TLV, AAPL, VWCE.DE): ").strip().upper()
                        if not ticker: continue
                        
                        tip = input(" Este activ manual (BVB/Tradeville)? (y/n): ").strip().lower()
                        is_manual = (tip == 'y')
                        
                        try:
                            qty = float(input(" Cantitate (Qty): "))
                            avg_price = float(input(" Preț Mediu de Cumpărare: "))
                            current_price = 0.0
                            currency = "USD"
                            is_bond = False
                            
                            if is_manual:
                                current_price = float(input(" Preț Curent de Piață: "))
                                currency = input(" Monedă (RON/EUR/USD) [implicit RON]: ").strip().upper()
                                if not currency: currency = "RON"
                                obligațiune = input(" Este obligațiune/titlu de stat? (y/n): ").strip().lower()
                                is_bond = (obligațiune == 'y')
                            else:
                                currency = input(" Monedă (EUR/USD) [implicit EUR]: ").strip().upper()
                                if not currency: currency = "EUR"
                                
                            portfolio_mgr.add_or_update_asset(ticker, qty, avg_price, is_manual, current_price, currency, is_bond)
                            print(f"\n{dashboard.GREEN} Activul {ticker} a fost adăugat cu succes și salvat în config.json!{dashboard.RESET}")
                        except ValueError:
                            print(f"\n{dashboard.RED} Eroare: Date numerice invalide!{dashboard.RESET}")
                        time.sleep(2)
                        
                    elif p_opt == '3':
                        dashboard.clear_screen()
                        print(f"{dashboard.BOLD}{dashboard.YELLOW}══✏️ MODIFICARE ACTIV ══════════════════════════════════════════════════════════{dashboard.RESET}")
                        ticker = input(" Introdu ticker-ul pe care vrei să îl modifici: ").strip().upper()
                        if not ticker: continue
                        
                        is_manual = False
                        asset_info = None
                        
                        if ticker in portfolio_mgr.auto_assets:
                            asset_info = portfolio_mgr.auto_assets[ticker]
                            is_manual = False
                        elif ticker in portfolio_mgr.manual_assets:
                            asset_info = portfolio_mgr.manual_assets[ticker]
                            is_manual = True
                            
                        if not asset_info:
                            print(f"\n{dashboard.RED} Activul {ticker} nu a fost găsit în portofoliu!{dashboard.RESET}")
                            time.sleep(2)
                            continue
                            
                        print(f" Date actuale: Cantitate={asset_info['qty']}, Preț Mediu={asset_info['avg_price']}")
                        try:
                            qty = input(f" Noua Cantitate [ENTER pentru neschimbat: {asset_info['qty']}]: ").strip()
                            qty = float(qty) if qty else asset_info['qty']
                            
                            avg_price = input(f" Noul Preț Mediu [ENTER pentru neschimbat: {asset_info['avg_price']}]: ").strip()
                            avg_price = float(avg_price) if avg_price else asset_info['avg_price']
                            
                            current_price = asset_info.get('current_price', 0.0)
                            if is_manual:
                                c_price = input(f" Noul Preț Curent [ENTER pentru neschimbat: {current_price}]: ").strip()
                                current_price = float(c_price) if c_price else current_price
                                
                            portfolio_mgr.add_or_update_asset(
                                ticker, qty, avg_price, is_manual, current_price, 
                                asset_info.get('currency', 'USD'), asset_info.get('is_bond', False)
                            )
                            print(f"\n{dashboard.GREEN} Activul {ticker} a fost actualizat cu succes în config.json!{dashboard.RESET}")
                        except ValueError:
                            print(f"\n{dashboard.RED} Eroare: Valori numerice invalide!{dashboard.RESET}")
                        time.sleep(2)
                        
                    elif p_opt == '4':
                        dashboard.clear_screen()
                        print(f"{dashboard.BOLD}{dashboard.YELLOW}══⚡ ACTUALIZARE RAPIDĂ PREȚURI BVB ════════════════════════════════════════════{dashboard.RESET}")
                        if not portfolio_mgr.manual_assets:
                            print(f"\n{dashboard.RED} Nu ai active manuale (BVB) în portofoliu!{dashboard.RESET}")
                            time.sleep(2)
                            continue
                        
                        print(" Activele tale de pe BVB:")
                        for t, info in portfolio_mgr.manual_assets.items():
                            print(f"  • {dashboard.BOLD}{t:<8}{dashboard.RESET} -> Preț curent salvat: {info['current_price']} {info['currency']}")
                        
                        ticker_bvb = input("\n Introdu ticker-ul pe care vrei să-l actualizezi (ex: SNP): ").strip().upper()
                        if ticker_bvb in portfolio_mgr.manual_assets:
                            info = portfolio_mgr.manual_assets[ticker_bvb]
                            new_p_input = input(f" Introdu noul preț curent pentru {ticker_bvb} (Curent: {info['current_price']}): ").strip()
                            if new_p_input:
                                try:
                                    portfolio_mgr.add_or_update_asset(
                                        ticker_bvb, info['qty'], info['avg_price'], True, 
                                        float(new_p_input), info['currency'], info.get('is_bond', False)
                                    )
                                    print(f"\n{dashboard.GREEN} Prețul pentru {ticker_bvb} a fost actualizat la {new_p_input} RON!{dashboard.RESET}")
                                except ValueError:
                                    print(f"\n{dashboard.RED} Eroare: Preț invalid!{dashboard.RESET}")
                        else:
                            if ticker_bvb:
                                print(f"\n{dashboard.RED} Ticker-ul introdus nu este un activ manual de pe BVB!{dashboard.RESET}")
                        time.sleep(2)

                    elif p_opt == '5':
                        dashboard.clear_screen()
                        print(f"{dashboard.BOLD}{dashboard.YELLOW}══❌ ȘTERGERE ACTIV ════════════════════════════════════════════════════════════{dashboard.RESET}")
                        ticker = input(" Introdu ticker-ul pe care vrei să îl ștergi definitiv: ").strip().upper()
                        if ticker:
                            confirma = input(f" Sigur vrei să ștergi {ticker}? (y/n): ").strip().lower()
                            if confirma == 'y':
                                if portfolio_mgr.remove_asset(ticker):
                                    print(f"\n{dashboard.GREEN} Activul {ticker} a fost șters definitiv din config.json!{dashboard.RESET}")
                                else:
                                    print(f"\n{dashboard.RED} Activul {ticker} nu a fost găsit!{dashboard.RESET}")
                            else:
                                print("\n Operațiune anulată.")
                        time.sleep(2)
                    elif p_opt == '6' or p_opt == '':
                        in_p_menu = False
                
                with data_lock:
                    portfolio_data = portfolio_mgr.get_portfolio_data()
                trigger_render(dashboard)
            else:
                trigger_render(dashboard)
        except (KeyboardInterrupt, EOFError):
            running = False
            sys.exit(0)

if __name__ == "__main__":
    main()