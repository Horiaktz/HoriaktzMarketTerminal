cd "$HOME\Desktop\HoriaktzMarketTerminal"

# Verificăm dacă există mediul virtual și îl activăm
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    .\.venv\Scripts\Activate.ps1
}

# Lansăm terminalul tău bursier
python market.py