import requests
from bs4 import BeautifulSoup


BVB_MAP = {
    "H2O": "ROH2O",
    "SNP": "ROSNP",
    "TLV": "ROTLV",
}


def get_bvb_price(symbol):

    try:
        code = BVB_MAP.get(symbol)

        if not code:
            return None, None

        url = f"https://m.bvb.ro/FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s={code}"

        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")

        price = soup.find("span", {"id": "ctl00_cph1_lblLastPrice"})
        change = soup.find("span", {"id": "ctl00_cph1_lblChangePercent"})

        if not price:
            return None, None

        price = float(price.text.replace(",", "."))
        change = float(change.text.replace("%", "").replace(",", "."))

        return price, change

    except:
        return None, None