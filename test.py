# type: ignore[attr-defined]
import MetaTrader5 as mt5
import time
from datetime import datetime

# === CONFIGURATION ===
ACCOUNT = 192846215  # Replace with your MT5 account number
PASSWORD = "Shahzaib.786"  # Replace with your MT5 password
SERVER = "Exness-MT5Trial"  # Replace with your broker's server name
SYMBOL = "XAUUSDm"
LOT_SIZE = 0.01
POINT_DIFFERENCE = 3  # TP/SL = ±3 points from entry
TRADE_INTERVAL = 900  # 15 minutes in seconds
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
        print(f"[{datetime.now()}] ⚠️ Symbol '{SYMBOL}' not found")
        return False

    if not symbol_info.visible:
        if not mt5.symbol_select(SYMBOL, True):
            print(f"[{datetime.now()}] ⚠️ Failed to select symbol '{SYMBOL}'")
            return False
    return True

# === CHECK IF TRADE IS OPEN ===
def is_trade_open():
    positions = mt5.positions_get(symbol=SYMBOL)
    return positions is not None and len(positions) > 0

# === CLOSE ALL OPEN TRADES FOR SYMBOL ===
def close_all_open_trades():
    positions = mt5.positions_get(symbol=SYMBOL)
    if not positions:
        print(f"[{datetime.now()}] ✅ No open trades to close.")
        return

    print(f"[{datetime.now()}] 🔄 Closing {len(positions)} open trade(s)...")

    for pos in positions:
        close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        lot = pos.volume
        price = mt5.symbol_info_tick(SYMBOL).bid if close_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(SYMBOL).ask

        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": lot,
            "type": close_type,
            "position": pos.ticket,
            "price": price,
            "deviation": 10,
            "magic": MAGIC_NUMBER,
            "comment": "Auto-close trade",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(close_request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"[{datetime.now()}] ✅ Closed trade #{pos.ticket}")
        else:
            print(f"[{datetime.now()}] ❌ Failed to close trade #{pos.ticket} | Code: {result.retcode}")

# === EXECUTE BUY ORDER ===
def execute_buy_order():
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        print(f"[{datetime.now()}] ⚠️ Failed to get tick data for {SYMBOL}")
        return

    ask_price = tick.ask
    tp = round(ask_price + POINT_DIFFERENCE, 2)
    sl = round(ask_price - POINT_DIFFERENCE, 2)

    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT_SIZE,
        "type": mt5.ORDER_TYPE_BUY,
        "price": ask_price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": MAGIC_NUMBER,
        "comment": "AutoBot XAUUSDm 3pt",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(order_request)
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"[{datetime.now()}] ❌ Order failed | Code: {getattr(result, 'retcode', 'N/A')} | Message: {getattr(result, 'comment', 'No comment')}")
    else:
        print(f"[{datetime.now()}] ✅ BUY Order Placed | Entry: {ask_price}, TP: {tp}, SL: {sl}")

# === MAIN BOT LOOP ===
def run_bot():
    while True:
        print(f"[{datetime.now()}] 🔁 Checking trade status...")

        if is_trade_open():
            print(f"[{datetime.now()}] ⏳ Trade already open. Attempting to close...")
            close_all_open_trades()
            time.sleep(2)

        print(f"[{datetime.now()}] 📥 Placing new BUY order...")
        execute_buy_order()

        print(f"[{datetime.now()}] ⏸️ Waiting {TRADE_INTERVAL // 60} minutes before next trade...\n")
        time.sleep(TRADE_INTERVAL)

# === ENTRY POINT ===
if __name__ == "__main__":
    if initialize() and validate_symbol():
        run_bot()

    mt5.shutdown()
