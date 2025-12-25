import yfinance as yf
import pandas as pd

def get_stock_data(ticker):
    # Auto-fix for Indian stocks if suffix is missing
    if ".NS" not in ticker and ".BO" not in ticker and "-" not in ticker:
        ticker += ".NS"
    
    stock = yf.Ticker(ticker)
    df = stock.history(period="3mo")
    return df, ticker

def calculate_indicators(df):
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    latest = df.iloc[-1]
    price = latest['Close']
    sma = latest['SMA_50']
    rsi = latest['RSI']

    # --- NEW NEUTRAL LOGIC ---
    # 1. Price vs SMA Neutral Zone: within 0.5% of the average
    if abs(price - sma) / sma < 0.005:
        trend = "Neutral"
    elif price > sma:
        trend = "Bullish"
    else:
        trend = "Bearish"

    # 2. RSI Neutral Zone: between 45 and 55
    rsi_signal = "Neutral"
    if rsi > 55: rsi_signal = "Bullish"
    if rsi < 45: rsi_signal = "Bearish"

    return {
        "price": round(price, 2),
        "rsi": round(rsi, 2),
        "sma_50": round(sma, 2),
        "trend": trend,
        "rsi_signal": rsi_signal
    }

def get_tech_analysis(ticker):
    print(f"📊 Tech Agent: Fetching live data for {ticker}...")
    df, final_ticker = get_stock_data(ticker)
    
    if df is None or df.empty:
        return {"signal": "Error", "price": 0, "detail": f"Ticker {ticker} not found"}
        
    indicators = calculate_indicators(df)
    return {
        "ticker": final_ticker,
        "signal": indicators['trend'],
        "price": indicators['price'],
        "confidence": f"RSI: {indicators['rsi']}",
        "detail": f"SMA50: {indicators['sma_50']}"
    }

def get_detailed_stock_info(ticker):
    stock = yf.Ticker(ticker)

    try:
        info = stock.info or {}
    except:
        info = {}

    hist = stock.history(period="1mo")

    # ---- SAFE PRICE RESOLUTION ----
    price = info.get("currentPrice")

    if price is None:
        if hist is not None and not hist.empty:
            price = hist['Close'].iloc[-1]
        else:
            price = 0  # ultimate fallback

    return {
        "price": round(price, 2) if price else 0,
        "change_pct": round(info.get("regularMarketChangePercent", 0), 2),
        "open": round(info.get("regularMarketOpen", 0), 2),
        "day_high": round(info.get("dayHigh", 0), 2),
        "day_low": round(info.get("dayLow", 0), 2),
        "volume": info.get("volume", 0),
        "avg_volume": info.get("averageVolume", 0),
        "mkt_cap": info.get("marketCap", 0),
        "pe_ratio": info.get("trailingPE", "N/A"),
        "high_52": info.get("fiftyTwoWeekHigh", 0),
        "low_52": info.get("fiftyTwoWeekLow", 0),
        "currency": info.get("currency", "INR")
    }

