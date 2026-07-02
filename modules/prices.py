import yfinance as yf
import contextlib
import io


def get_price(symbol):
    try:
        f = io.StringIO()

        with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
            ticker = yf.Ticker(symbol)

            info = ticker.fast_info
            price = info["lastPrice"]

            hist = ticker.history(period="2d")

        if len(hist) < 2:
            return None, None

        previous = hist["Close"].iloc[-2]

        change = ((price - previous) / previous) * 100

        return round(price, 2), round(change, 2)

    except:
        return None, None