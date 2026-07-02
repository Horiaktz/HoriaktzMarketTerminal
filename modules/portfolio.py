# PORTOFOLIU LIVE (ETF-uri + externe)
PORTFOLIO = {
    "VWCE.DE": {"qty": 12.5, "avg_price": 150.0},
    "IUSN.DE": {"qty": 58, "avg_price": 8.5},
    "VVSM.DE": {"qty": 4, "avg_price": 95.0},
}


# BVB DOAR MANUAL (fără API, fără erori)
BVB_HOLDINGS = {
    "H2O": 8,
    "SNP": 1152,
    "TLV": 35,
}


def get_portfolio():
    return PORTFOLIO


def get_bvb():
    return BVB_HOLDINGS