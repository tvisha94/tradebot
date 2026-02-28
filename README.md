# Tradebot CLI (Binance Futures Testnet)

Crux: A minimalist CLI to place orders on USDT-M Binance Testnet.

### Setup
* **Clone:** `git clone https://github.com/tvisha94/tradebot.git`
* **Deps:** `pip install -r requirements.txt`
* **Keys:** Create `.env` with `BINANCE_TESTNET_API_KEY` & `BINANCE_TESTNET_API_SECRET`.

### Run
* **Market Buy:** `python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001`
* **Limit Sell:** `python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 60000`

### Crux Facts
* **Env:** Hardcoded to Binance Futures Testnet.
* **Side:** Supports BUY/SELL.
* **Type:** MARKET/LIMIT (GTC).
* **Asset:** USDT-M pairs only.
* **Logs:** Recorded in `logs/tradebot.log`.
