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
is_in_sub_menu = False

def data_fetcher_loop(indices_mgr, movers_mgr, news_mgr, portfolio_mgr, converter, dashboard):
    global indices_data, movers_data, news_data, portfolio_data, currency_rates, running, is_in_sub_menu
    
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
            
            if not is_in_sub_menu:
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

def get_default_months(ticker, is_bond):
    """Returnează lunile în care încasezi bani în mod tradițional bazat pe ticker"""
    t = ticker.upper()
    if is_bond:
        # Obligațiunile de tip BNET plătesc de regulă cupoane trimestriale sau semestriale
        if "BNET" in t:
            return ["Martie", "Iunie", "Septembrie", "Decembrie"]
        return ["Iunie", "Decembrie"]
    else:
        # Acțiunile mari de pe BVB au distribuit istoric dividendele în lunile de vară
        if "SNP" in t:
            return ["Iunie"]
        if "TLV" in t:
            return ["Mai"]
        return ["Iunie"]

def main():
    global running, indices_data, movers_data, news_data, portfolio_data, currency_rates, is_in_sub_menu
    
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
                is_in_sub_menu = True
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
                is_in_sub_menu = False
                trigger_render(dashboard)
            elif cmd == 'p':
                in_p_menu = True
                is_in_sub_menu = True
                while in_p_menu:
                    dashboard.clear_screen()
                    print(f"{dashboard.BOLD}{dashboard.YELLOW}══💼 MENIU MANAGE PORTFOLIO ════════════════════════════════════════════════════{dashboard.RESET}")
                    print(f" 1. {dashboard.CYAN}Vizualizează Alocarea Activelor{dashboard.RESET} (Grafic ASCII pe ponderi)")
                    print(f" 2. {dashboard.CYAN}Adaugă Activ Nou{dashboard.RESET} (XTB sau Tradeville/BVB)")
                    print(f" 3. {dashboard.CYAN}Modifică / Actualizează Complet un Activ{dashboard.RESET}")
                    print(f" 4. {dashboard.CYAN}Actualizează Rapid Prețuri BVB (Manual){dashboard.RESET}")
                    print(f" 5. {dashboard.MAGENTA}Raport Istoric Dividende & Cupoane BVB{dashboard.RESET} 📅 💰")
                    print(f" 6. {dashboard.RED}Șterge un Activ{dashboard.RESET}")
                    print(f" 7. {dashboard.GREEN}Înapoi la Dashboard{dashboard.RESET}")
                    print(f"{dashboard.BOLD}{dashboard.YELLOW}════════════════════════════════════════════════════════════════════════════════{dashboard.RESET}")
                    sys.stdout.write(f"\n Selectează o opțiune (1-7): ")
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
                        ticker = input(" Introdu Ticker (ex: SNP, TLV, BNET, VWCE.DE): ").strip().upper()
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
                                obligațiune = input(" Este obligațiune/titlu de stat (ex: BNET)? (y/n): ").strip().lower()
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
                                print(f"\n{dashboard.RED} Ticker-ul introdus nu este un active manual de pe BVB!{dashboard.RESET}")
                        time.sleep(2)

                    elif p_opt == '5':
                        in_sub_loop = True
                        while in_sub_loop:
                            dashboard.clear_screen()
                            print(f"{dashboard.BOLD}{dashboard.YELLOW}══📅 SELECTARE COMPARTIMENT AN BAZĂ DE DATE ═════════════════════════════════════{dashboard.RESET}")
                            print(" 1. Vizualizează/Editează istoric [ Anul 2026 ] (Încasat deja)")
                            print(" 2. Vizualizează/Editează planificări [ Anul 2027 ] (În pregătire 🚀)")
                            print(" 3. Înapoi la meniul principal")
                            an_selectat = input("\n Selectează opțiunea (1-3): ").strip()
                            
                            if an_selectat == '3':
                                in_sub_loop = False
                                continue
                                
                            an_str = "2027" if an_selectat == '2' else "2026"
                            
                            dashboard.clear_screen()
                            print(f"{dashboard.BOLD}{dashboard.YELLOW}══💰 RAPORT CASHFLOW BVB - ANUL {an_str} ═══════════════════════════════════════════{dashboard.RESET}")
                            if not portfolio_mgr.manual_assets:
                                print(f"\n{dashboard.RED} Nu ai active pe BVB adăugate în portofoliu!{dashboard.RESET}")
                                input("\nApasă ENTER pentru înapoi...")
                                in_sub_loop = False
                                continue
                            
                            print(f"  {dashboard.BOLD}{dashboard.WHITE}{'TICKER':<10}{'TIP':<12}{'HIST. QTY':<12}{'CASH/UNIT':<15}{'TOTAL ÎNCASAT'}{dashboard.RESET}")
                            print(f"  {'-'*70}")
                            
                            total_an_ron = 0.0
                            monthly_distribution = {m: 0.0 for m in ["Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie", "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"]}
                            
                            for t, info in portfolio_mgr.manual_assets.items():
                                is_bond = info.get('is_bond', False)
                                tip_text = "Obligațiune" if is_bond else "Acțiune"
                                
                                matrix = info.get('history_matrix', {})
                                year_data = matrix.get(an_str, {})
                                
                                hist_qty = year_data.get('qty', info['qty'])
                                cash_per_unit = year_data.get('cash', info.get('dps', 0.0) if an_str == "2026" else 0.0)
                                
                                total_asset_cash = hist_qty * cash_per_unit
                                total_an_ron += total_asset_cash
                                
                                # Distribuim banii pe luni în mod inteligent
                                active_months = get_default_months(t, is_bond)
                                cash_per_month = total_asset_cash / len(active_months) if active_months else 0.0
                                for m in active_months:
                                    monthly_distribution[m] += cash_per_month
                                
                                print(f"  {dashboard.BOLD}{t:<10}{dashboard.RESET}{tip_text:<12}{hist_qty:<12,g}{cash_per_unit:<15,.4f}{total_asset_cash:,.2f} RON")
                            
                            print(f"  {'-'*70}")
                            print(f"  {dashboard.BOLD}TOTAL CASHFLOW ÎNCASAT/ESTIMAT ÎN {an_str}: {dashboard.GREEN}{total_an_ron:,.2f} RON{dashboard.RESET}")
                            
                            print(f"\n {dashboard.BOLD}{dashboard.YELLOW}[ OPȚIUNI ADIȚIONALE ]{dashboard.RESET}")
                            print(f"  {dashboard.CYAN}v{dashboard.RESET} = Vizualizează Calendarul Lunar de Cashflow 📅")
                            print(f"  {dashboard.CYAN}e{dashboard.RESET} = Editează valorile acestui an")
                            print(f"  {dashboard.CYAN}b{dashboard.RESET} = Înapoi la selectare an")
                            
                            sub_cmd = input("\n Alege o acțiune: ").strip().lower()
                            
                            if sub_cmd == 'v':
                                dashboard.clear_screen()
                                print(f"{dashboard.BOLD}{dashboard.YELLOW}══📅 CALENDAR CASHFLOW LUNAR ESTIMAT - ANUL {an_str} ════════════════════════════{dashboard.RESET}")
                                max_val = max(monthly_distribution.values()) if max(monthly_distribution.values()) > 0 else 1.0
                                
                                for month, amount in monthly_distribution.items():
                                    if amount > 0:
                                        bars_count = int((amount / max_val) * 15)
                                        bars_count = 1 if bars_count == 0 else bars_count
                                        bar_str = "█" * bars_count
                                        print(f"  {month:<12} | {dashboard.GREEN}{bar_str:<15}{dashboard.RESET} | {dashboard.BOLD}{amount:>8,.2f} RON{dashboard.RESET}")
                                    else:
                                        print(f"  {month:<12} | {' ' * 15} | {dashboard.WHITE}0.00 RON{dashboard.RESET}")
                                print(f"  {'-'*65}")
                                print(f"  {dashboard.BOLD}Total Anual Dinamic: {dashboard.GREEN}{total_an_ron:,.2f} RON{dashboard.RESET}")
                                input(f"\nApasă ENTER pentru a te întoarce la raportul {an_str}...")
                                
                            elif sub_cmd == 'e':
                                edit_t = input("\n Introdu ticker-ul pe care vrei să îl modifici: ").strip().upper()
                                if edit_t in portfolio_mgr.manual_assets:
                                    info = portfolio_mgr.manual_assets[edit_t]
                                    if 'history_matrix' not in info:
                                        portfolio_mgr.manual_assets[edit_t]['history_matrix'] = {}
                                    if an_str not in portfolio_mgr.manual_assets[edit_t]['history_matrix']:
                                        portfolio_mgr.manual_assets[edit_t]['history_matrix'][an_str] = {
                                            "qty": info['qty'],
                                            "cash": info.get('dps', 0.0)
                                        }
                                        
                                    current_matrix_data = portfolio_mgr.manual_assets[edit_t]['history_matrix'][an_str]
                                    
                                    try:
                                        input_qty = input(f" Cantitate deținută în {an_str} [ENTER pentru neschimbat: {current_matrix_data['qty']}]: ").strip()
                                        new_qty = float(input_qty) if input_qty else current_matrix_data['qty']
                                        
                                        tip_prompt = "cupon per obligațiune" if info.get('is_bond', False) else "dividend net per acțiune (DPS)"
                                        input_cash = input(f" Valoare {tip_prompt} în {an_str} [ENTER pentru neschimbat: {current_matrix_data['cash']}]: ").strip()
                                        new_cash = float(input_cash) if input_cash else current_matrix_data['cash']
                                        
                                        portfolio_mgr.manual_assets[edit_t]['history_matrix'][an_str] = {
                                            "qty": new_qty,
                                            "cash": new_cash
                                        }
                                        portfolio_mgr.save_portfolio()
                                        print(f"\n{dashboard.GREEN} Succes! Datele istorice pentru {edit_t} ({an_str}) au fost actualizate!{dashboard.RESET}")
                                        time.sleep(1.5)
                                    except ValueError:
                                        print(f"\n{dashboard.RED} Eroare: Introdu doar valori numerice valide!{dashboard.RESET}")
                                        time.sleep(1.5)
                                else:
                                    print(f"\n{dashboard.RED} Ticker-ul nu există!{dashboard.RESET}")
                                    time.sleep(1.5)
                            elif sub_cmd == 'b':
                                continue

                    elif p_opt == '6':
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
                    elif p_opt == '7' or p_opt == '':
                        in_p_menu = False
                
                is_in_sub_menu = False
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