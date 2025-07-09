# type: ignore[attr-defined]
import MetaTrader5 as mt5
import time
from datetime import datetime

# === CONFIGURATION ===
ACCOUNT = 192846215             # Replace with your MT5 account number
PASSWORD = "Shahzaib.786"       # Replace with your MT5 password
SERVER = "Exness-MT5Trial"      # Replace with your broker's server name
SYMBOL = "XAUUSDm"              # Make sure this matches exactly in Market Watch
LOT_SIZE = 0.01
TRADE_INTERVAL = 900            # 15 minutes in seconds
MAGIC_NUMBER = 123456

# === INITIALIZE METATRADER ===
def initialize():
    if not mt5.initialize(login=ACCOUNT, password=PASSWORD, server=SERVER):
        print(f"[{datetime.now()}] ❌ MT5 initialization failed: {mt5.last_error()}")
        return False

    print(f"[{datetime.now()}] ✅ Connected to MetaTrader 5")
    return True

# === CHECK SYMBOL VALIDITY ===
def validate_symbol():
    symbol_info = mt5.symbol_info(SYMBOL)

    if symbol_info is None:
        print(f"[{datetime.now()}] ⚠️ '{SYMBOL}' not found")
        return False
    if not symbol_info.visible:
        if not mt5.symbol_select(SYMBOL, True):
            print(f"[{datetime.now()}] ⚠️ '{SYMBOL}' not visible and could not be selected")
            return False
    return True

# === CHECK IF ANY TRADE IS OPEN ===
def is_trade_open():
    positions = mt5.positions_get(symbol=SYMBOL)
    if positions is None:
        return False
    return len(positions) > 0

# === PLACE BUY TRADE ===
def execute_buy_order():
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        print(f"[{datetime.now()}] ⚠️ Failed to get price data for {SYMBOL}")
        return

    ask_price = tick.ask
    tp = round(ask_price + 0.3, 2)
    sl = 0  # No Stop Loss

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT_SIZE,
        "type": mt5.ORDER_TYPE_BUY,
        "price": ask_price,
        "sl": sl,  # SL removed
        "tp": tp,  # TP set to +0.3
        "deviation": 10,
        "magic": MAGIC_NUMBER,
        "comment": "AutoBot XAUUSD TP 0.3 no SL",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"[{datetime.now()}] ❌ Order failed: Code={getattr(result, 'retcode', 'N/A')}, Message={getattr(result, 'comment', 'No result')}")
    else:
        print(f"[{datetime.now()}] ✅ BUY Order Placed | Entry: {ask_price}, TP: {tp}")

# === MAIN BOT LOOP ===
def run_bot():
    while True:
        print(f"[{datetime.now()}] 🔁 Checking trade status...")

        if not is_trade_open():
            print(f"[{datetime.now()}] 📥 No open trade. Executing new BUY order...")
            execute_buy_order()
        else:
            print(f"[{datetime.now()}] ⏳ Trade already open. Waiting...")

        time.sleep(TRADE_INTERVAL)

# === STARTUP ===
if __name__ == "__main__":
    if initialize() and validate_symbol():
        run_bot()

    mt5.shutdown()
