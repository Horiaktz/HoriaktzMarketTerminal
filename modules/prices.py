import yfinance as yf

class PricesManager:
    def __init__(self):
        pass

    def get_live_price(self, ticker):
        """Returnează prețul live, cu timeout strict pentru a preveni blocarea."""
        try:
            t = yf.Ticker(ticker)
            # Folosim un timeout scurt în istoric
            hist = t.history(period="1d", timeout=3)
            if not hist.empty:
                return round(hist['Close'].iloc[-1], 2)
            return None
        except Exception:
            return None

    def get_multiple_prices(self, tickers_list):
        prices = {}
        for ticker in tickers_list:
            price = self.get_live_price(ticker)
            if price is not None:
                prices[ticker] = price
        return prices