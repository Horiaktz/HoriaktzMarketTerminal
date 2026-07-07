import json
import os
import getpass
import requests
from datetime import datetime
from modules.prices import PricesManager
from modules.utils import CurrencyConverter

class PortfolioManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.prices_manager = PricesManager()
        self.converter = CurrencyConverter()
        self.auto_assets = {}
        self.manual_assets = {}
        self.total_deposited_ron = 10630.0
        self.daily_history = {} # Structura noua: {"YYYY-MM-DD": {"value": 12000, "comment": "Depus 100 RON XTB"}}
        
        # Parola secretă pentru PC-uri străine
        self.SECRET_PASSWORD = "Horia2026"
        
        self.load_portfolio()

    def load_portfolio(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    self.auto_assets = data.get("auto_assets", {})
                    self.manual_assets = data.get("manual_assets", {})
                    self.total_deposited_ron = data.get("total_deposited_ron", 10630.0)
                    self.daily_history = data.get("daily_history", {})
            except Exception:
                self._set_default_portfolio()
        else:
            self._set_default_portfolio()

    def _set_default_portfolio(self):
        self.auto_assets = {}
        self.manual_assets = {}
        self.total_deposited_ron = 10630.0
        self.daily_history = {}
        self.save_portfolio()

    def save_portfolio(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump({
                    "auto_assets": self.auto_assets,
                    "manual_assets": self.manual_assets,
                    "total_deposited_ron": self.total_deposited_ron,
                    "daily_history": self.daily_history
                }, f, indent=4)
        except Exception:
            pass

    def import_horia_vault(self):
        print("\n\033[33m[🔒 SECURITATE] Se accesează Seiful Privat al lui Horia.\033[0m")
        incercare = getpass.getpass(" Introdu parola master de deblocare: ")
        
        if incercare == self.SECRET_PASSWORD:
            try:
                print("[*] Se descarcă datele securizate...")
                url = "https://raw.githubusercontent.com/Horiaktz/HoriaktzMarketTerminal/main/config.json"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.auto_assets = data.get("auto_assets", {})
                    self.manual_assets = data.get("manual_assets", {})
                    self.total_deposited_ron = data.get("total_deposited_ron", 10630.0)
                    self.daily_history = data.get("daily_history", {})
                    
                    self.save_portfolio()
                    print("\033[32m[🔓 ACCESS GRANTED] Portofoliul tău master a fost importat cu succes!\033[0m")
                    return True
                else:
                    print("\033[31m[❌] Nu s-a putut descărca seiful de pe GitHub (Eroare Server).\033[0m")
                    return False
            except Exception as e:
                print(f"\033[31m[❌] Eroare la procesarea datelor: {e}\033[0m")
                return False
        else:
            print("\033[31m[❌ ACCESS DENIED] Parolă incorectă! Seiful rămâne închis.\033[0m")
            return False

    def check_and_record_daily_value(self):
        """Rulează în fundal. Înregistrează valoarea portofoliului o singură dată pe zi la ora 18:00"""
        acum = datetime.now()
        today_str = acum.strftime("%Y-%m-%d")
        
        if acum.hour >= 18 and today_str not in self.daily_history:
            total_current_value_ron = 0.0
            rates = self.converter.get_rates()
            eur_ron = rates.get('EUR_RON', 5.23)
            
            for ticker, info in self.auto_assets.items():
                live_price_eur = self.prices_manager.get_live_price(ticker)
                if live_price_eur is None: live_price_eur = info['avg_price']
                total_current_value_ron += (info['qty'] * live_price_eur) * eur_ron
                
            for ticker, info in self.manual_assets.items():
                total_current_value_ron += info['qty'] * info['current_price']
                
            if total_current_value_ron > 0:
                self.daily_history[today_str] = {
                    "value": round(total_current_value_ron, 2),
                    "comment": ""
                }
                self.save_portfolio()

    def add_history_comment(self, date_str, comment_text):
        """Adaugă sau modifică un comentariu pentru o dată specifică din istoric"""
        if date_str in self.daily_history:
            # Dacă nodul vechi era doar un simplu număr (migrare de date vechi), îl convertim
            if not isinstance(self.daily_history[date_str], dict):
                self.daily_history[date_str] = {"value": self.daily_history[date_str], "comment": ""}
                
            self.daily_history[date_str]["comment"] = comment_text
            self.save_portfolio()
            return True
        return False

    def add_or_update_asset(self, ticker, qty, avg_price, is_manual=False, current_price=0.0, currency="USD", is_bond=False):
        if is_manual:
            old_dps = self.manual_assets.get(ticker.upper(), {}).get("dps", 0.0)
            old_matrix = self.manual_assets.get(ticker.upper(), {}).get("history_matrix", {})
            self.manual_assets[ticker.upper()] = {
                "qty": float(qty),
                "avg_price": float(avg_price),
                "current_price": float(current_price if current_price > 0 else avg_price),
                "currency": currency.upper(),
                "is_bond": is_bond,
                "dps": old_dps,
                "history_matrix": old_matrix
            }
        else:
            old_dps = self.auto_assets.get(ticker.upper(), {}).get("dps", 0.0)
            self.auto_assets[ticker.upper()] = {
                "qty": float(qty),
                "avg_price": float(avg_price),
                "currency": currency.upper(),
                "dps": old_dps
            }
        self.save_portfolio()

    def remove_asset(self, ticker):
        ticker = ticker.upper()
        removed = False
        if ticker in self.auto_assets:
            del self.auto_assets[ticker]
            removed = True
        elif ticker in self.manual_assets:
            del self.manual_assets[ticker]
            removed = True
        if removed:
            self.save_portfolio()
        return removed

    def get_total_deposited_ron(self):
        return self.total_deposited_ron

    def get_portfolio_data(self):
        portfolio_rows = []
        rates = self.converter.get_rates()
        usd_ron = rates.get('USD_RON', 4.57)
        eur_ron = rates.get('EUR_RON', 5.23)
        
        eur_to_usd = eur_ron / usd_ron
        ron_to_usd = 1.0 / usd_ron

        for ticker, info in self.auto_assets.items():
            live_price_eur = self.prices_manager.get_live_price(ticker)
            if live_price_eur is None: live_price_eur = info['avg_price']
            qty = info['qty']
            value_eur = qty * live_price_eur
            cost_basis_eur = qty * info['avg_price']
            pnl_eur = value_eur - cost_basis_eur
            pnl_pct = (pnl_eur / cost_basis_eur) * 100 if cost_basis_eur > 0 else 0.0

            portfolio_rows.append({
                'ticker': ticker.split('.')[0], 'qty': qty, 'price': round(live_price_eur, 2),
                'value': round(value_eur, 2), 'pnl_val': round(pnl_eur, 2), 'pnl_pct': round(pnl_pct, 2),
                'currency': info.get('currency', 'EUR'), 'value_usd': value_eur * eur_to_usd, 'pnl_usd': pnl_eur * eur_to_usd
            })
            
        for ticker, info in self.manual_assets.items():
            qty = info['qty']
            value_ron = qty * info['current_price']
            cost_basis_ron = qty * info['avg_price']
            pnl_ron = value_ron - cost_basis_ron
            pnl_pct = (pnl_ron / cost_basis_ron) * 100 if cost_basis_ron > 0 else 0.0

            portfolio_rows.append({
                'ticker': ticker, 'qty': qty, 'price': round(info['current_price'], 2),
                'value': round(value_ron, 2), 'pnl_val': round(pnl_ron, 2), 'pnl_pct': round(pnl_pct, 2),
                'currency': info.get('currency', 'RON'), 'value_usd': value_ron * ron_to_usd, 'pnl_usd': pnl_ron * ron_to_usd,
                'is_bond': info.get('is_bond', False), 'dps': info.get('dps', 0.0), 'history_matrix': info.get('history_matrix', {})
            })
            
        return portfolio_rows

    def generate_allocation_chart(self, portfolio_data):
        total_val = sum(item['value_usd'] for item in portfolio_data)
        if total_val == 0: return " Portofoliul este gol."
        chart_lines = ["\n Alocare Active (Pondere Valorică):", f" {'-'*45}"]
        for item in portfolio_data:
            weight = item['value_usd'] / total_val
            bar_str = "█" * int(weight * 20)
            chart_lines.append(f"  {item['ticker']:<8} | {bar_str:<20} | {weight*100:>5.1f}%")
        return "\n".join(chart_lines)