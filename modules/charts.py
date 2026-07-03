import yfinance as yf
from datetime import datetime

class ChartManager:
    def __init__(self):
        pass

    def draw_ascii_chart(self, ticker_symbol, days=20):
        """Descarcă datele și returnează un grafic ASCII sub formă de string"""
        try:
            ticker_symbol = ticker_symbol.strip().upper()
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="1mo")
            
            if hist.empty:
                return f"\n [Eroare] Nu s-au găsit date pentru ticker-ul [{ticker_symbol}]."

            closes = hist['Close'].tail(days).tolist()
            
            if len(closes) < 2:
                return f"\n [Eroare] Date insuficiente pentru [{ticker_symbol}]."

            min_val = min(closes)
            max_val = max(closes)
            val_range = max_val - min_val if max_val != min_val else 1

            height = 8  # Compactat la 8 linii ca să încapă mai multe pe ecran
            chart_lines = [[" " for _ in range(len(closes))] for _ in range(height)]

            for col, price in enumerate(closes):
                row = int((price - min_val) / val_range * (height - 1))
                row = (height - 1) - row
                chart_lines[row][col] = "●"

            output = []
            output.append(f"\n {ticker_symbol} | Ultimele {len(closes)} zile:")
            output.append(f" {'-'*45}")

            for r in range(height):
                current_row_val = max_val - (r * (val_range / (height - 1)))
                row_str = "".join(chart_lines[r])
                output.append(f"  ${current_row_val:>8.2f} | {row_str}")

            output.append(f"  {' '*10}| {'^'*len(closes)}")
            output.append(f"  Min: ${min_val:.2f}  |  Max: ${max_val:.2f}")
            output.append(f" {'='*45}")
            
            return "\n".join(output)

        except Exception as e:
            return f"\n Eroare la generarea graficului pentru {ticker_symbol}: {e}"