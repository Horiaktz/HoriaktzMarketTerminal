import yfinance as yf
import pandas as pd

class MoversManager:
    def __init__(self):
        # Folosim o listă extinsă de acțiuni tech/heavyweight populare pentru a detecta mișcările pieței
        self.watchlist = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD', 'PLTR', 'RIVN', 'NFLX', 'INTC']

    def get_market_movers(self):
        movers_data = []
        
        for ticker in self.watchlist:
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="2d")
                if len(hist) >= 2:
                    close_today = hist['Close'].iloc[-1]
                    close_yesterday = hist['Close'].iloc[-2]
                    pct_change = ((close_today - close_yesterday) / close_yesterday) * 100
                    
                    movers_data.append({
                        'ticker': ticker,
                        'price': round(close_today, 2),
                        'change': round(pct_change, 2)
                    })
            except Exception:
                continue
                
        # Dacă nu avem date, punem niște mock-uri ca să nu crape UI-ul
        if not movers_data:
            movers_data = [{'ticker': 'NODATA', 'price': 0.0, 'change': 0.0}]

        # Sortăm pentru Gainers și Losers
        sorted_movers = sorted(movers_data, key=lambda x: x['change'], reverse=True)
        
        gainers = [m for m in sorted_movers if m['change'] >= 0][:5]
        losers = [m for m in sorted_movers if m['change'] < 0][::-1][:5] # Cei mai negativi primii
        
        return {
            'gainers': gainers,
            'losers': losers
        }