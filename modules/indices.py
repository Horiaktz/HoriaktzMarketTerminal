import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class IndicesManager:
    def __init__(self):
        self.tickers = {
            'S&P 500': '^GSPC',
            'NASDAQ': '^IXIC',
            'DOW': '^DJI',
            'VIX': '^VIX'
        }

    def get_change(self, history, period_str):
        if history.empty or len(history) < 2:
            return 0.0
            
        current_price = history['Close'].iloc[-1]
        
        # Determinăm indexul din istoric în funcție de perioadă
        if period_str == '1H':
            # Notă: Pentru 1H e nevoie de date intraday, dacă istoricul e zilnic luăm penultima valoare ca proxy
            prev_price = history['Close'].iloc[-2] if len(history) > 1 else current_price
        elif period_str == '1D':
            prev_price = history['Close'].iloc[-2] if len(history) > 1 else current_price
        elif period_str == '1W':
            prev_price = history['Close'].iloc[-5] if len(history) > 4 else history['Close'].iloc[0]
        elif period_str == '1M':
            prev_price = history['Close'].iloc[-21] if len(history) > 20 else history['Close'].iloc[0]
        else:
            prev_price = current_price

        if prev_price == 0:
            return 0.0
            
        return ((current_price - prev_price) / prev_price) * 100

    def get_indices_data(self):
        data = {}
        for name, ticker in self.tickers.items():
            try:
                # Luăm istoric pe o lună pentru a avea destule zile pentru calculele de 1W și 1M
                ticker_obj = yf.Ticker(ticker)
                hist = ticker_obj.history(period="1mo")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    data[name] = {
                        'price': round(current_price, 2),
                        '1H': round(self.get_change(hist, '1H'), 2),
                        '1D': round(self.get_change(hist, '1D'), 2),
                        '1W': round(self.get_change(hist, '1W'), 2),
                        '1M': round(self.get_change(hist, '1M'), 2)
                    }
                else:
                    data[name] = {'price': 0.0, '1H': 0.0, '1D': 0.0, '1W': 0.0, '1M': 0.0}
            except Exception:
                data[name] = {'price': 0.0, '1H': 0.0, '1D': 0.0, '1W': 0.0, '1M': 0.0}
        return data