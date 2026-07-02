import yfinance as yf


# fallback safe (evită spam / erori)
INVALID = {"H2O", "SNP", "TLV"}


def get_price(symbol: str):

    if symbol in INVALID:
        return None, None

    try:
        ticker = yf.Ticker(symbol)

        hist = ticker.history(period="5d")

        if hist is None or len(hist) < 2:
            return None, None

        price = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2])

        change = ((price - prev) / prev) * 100 if prev else 0

        return price, change

    except:
        return None, None