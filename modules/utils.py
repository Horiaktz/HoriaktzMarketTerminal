import yfinance as yf

class CurrencyConverter:
    def __init__(self):
        self.usd_ron_ticker = "USDRON=X"
        self.eur_ron_ticker = "EURRON=X"
        # Actualizat fallback-ul la cotațiile curente din 2026
        self.default_rates = {'USD_RON': 4.57, 'EUR_RON': 5.23}

    def get_rates(self):
        """Returnează cursurile live pentru USD/RON și EUR/RON. În caz de eroare, dă fallback-uri stabile."""
        rates = {'USD_RON': 4.55, 'EUR_RON': 4.97} # Fallback de siguranță
        try:
            # Luăm USD/RON
            t_usd = yf.Ticker(self.usd_ron_ticker)
            hist_usd = t_usd.history(period="1d")
            if not hist_usd.empty:
                rates['USD_RON'] = hist_usd['Close'].iloc[-1]
            
            # Luăm EUR/RON
            t_eur = yf.Ticker(self.eur_ron_ticker)
            hist_eur = t_eur.history(period="1d")
            if not hist_eur.empty:
                rates['EUR_RON'] = hist_eur['Close'].iloc[-1]
                
        except Exception:
            pass # Mergem pe fallback dacă API-ul e blocat temporar
            
        return rates