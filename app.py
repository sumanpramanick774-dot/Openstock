
import streamlit as st
import requests
import pandas as pd
# ... আপনার বাকি সমস্ত কোড নিচে থাকবে ...

import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import os
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

# ফোল্ডার তৈরি (যেখানে প্রতিদিনের ডেটা সেভ হবে)
SAVE_DIR = "historical_data"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# ================================================================
# 1. STREAMLIT UI SETUP
# ================================================================
st.set_page_config(page_title="Dhan EOD Watchlist", layout="wide")
st.title("📈 Dhan EOD Intraday Watchlist")
st.markdown("Volume Momentum + Historical Rolling Option Chain (Private App)")

# Sidebar for API Inputs (কোড না ঘেঁটে এখান থেকেই টোকেন দেবেন)
st.sidebar.header("🔑 API Credentials")
ACCESS_TOKEN = st.sidebar.text_input("Access Token", type="password", help="Dhan HQ থেকে পাওয়া আজকের টোকেন পেস্ট করুন")
CLIENT_ID = st.sidebar.text_input("Client ID", value="1101908991")

# ================================================================
# 2. CONSTANTS & DICTIONARY
# ================================================================
BASE_URL = "https://api.dhan.co/v2"
HISTORICAL_URL = f"{BASE_URL}/charts/intraday"
ROLLING_OPTION_URL = f"{BASE_URL}/charts/rollingoption"

CASH_API_SLEEP = 0.5
OPTION_CHAIN_SLEEP = 2.0
MAX_RETRIES = 3

STOCKS = {
    "360ONE": "13061","ABB": "13","ABCAPITAL": "21614","ADANIENSOL": "10217","ADANIENT": "25",
    "ADANIGREEN": "3563","ADANIPORTS": "15083","ADANIPOWER": "17388","ALKEM": "11703",
    "AMBER": "1185","AMBUJACEM": "1270","ANANDRATHI": "7145","ANGELONE": "324",
    "APLAPOLLO": "25780","APOLLOHOSP": "157","ASHOKLEY": "212","ASIANPAINT": "236",
    "ASTRAL": "14418","ATHERENERG": "757645","AUBANK": "21238","AUROPHARMA": "275",
    "AXISBANK": "5900","BAJAJ-AUTO": "16669","BAJAJFINSV": "16675","BAJAJHLDNG": "305",
    "BAJFINANCE": "317","BANDHANBNK": "2263","BANKBARODA":"4668","BANKINDIA":"4745"
    ,"BDL": "2144","BEL": "383","BHARATFORG": "422","BHARTIARTL": "10604","BHEL": "438",
    "BIOCON": "11373","BLUESTARCO": "8311","BOSCHLTD": "2181","BPCL": "526","BSE": "19585",
    "BRITANNIA": "547","CAMS": "342","CANBK": "10794","CDSL": "21174","CGPOWER": "760",
    "CHOLAFIN": "685","CIPLA": "694","COALINDIA": "20374","COCHINSHIP": "21508","DABUR": "772",
    "COFORGE": "11543","COLPAL": "15141","CONCOR": "4749","CROMPTON": "17094",
    "CUMMINSIND": "1901","DELHIVERY": "9599","DIVISLAB": "10940","DIXON": "21690",
    "DLF": "14732","DMART": "19913","DRREDDY": "881","EICHERMOT": "910","ENRIN": "756871",
    "ETERNAL": "5097","FEDERALBNK": "1023","FORCEMOT": "11573","FORTIS": "14592",
    "GAIL": "4717","GLENMARK": "7406","GMRAIRPORT": "13528","GODFRYPHLP": "1181",
    "GODREJCP": "10099","GODREJPROP": "17875","GRASIM": "1232","GVT&D": "16783",
    "HAL": "2303","HAVELLS": "9819","HCLTECH": "7229","HDFCAMC": "4244","HDFCBANK": "1333",
    "HDFCLIFE": "467","HEROMOTOCO": "1348","HINDALCO": "1363","HINDPETRO": "1406",
    "HINDUNILVR": "1394","HINDZINC": "1424","HYUNDAI": "25844","ICICIBANK": "4963",
    "ICICIGI": "21770","ICICIPRULI": "18652","IDEA": "14366","IDFCFIRSTB": "11184",
    "IEX": "220","INDHOTEL": "1512","INDIANB": "14309","INDIGO": "11195","INDUSINDBK": "5258",
    "INDUSTOWER": "29135","INFY": "1594","INOXWIND": "7852","IOC": "1624","IREDA": "20261",
    "IRFC": "2029","ITC": "1660","JINDALSTEL": "6733","JIOFIN": "18143","JSWENERGY": "17869",
    "JSWSTEEL": "11723","JUBLFOOD": "18096","KALYANKJIL": "2955","KAYNES": "12092",
    "KEI": "13310","KFINTECH": "13359","KOTAKBANK": "1922","KPITTECH": "9683","LTF": "24948",
    "LAURUSLABS":"19234","LICHSGFIN": "1997","LICI": "9480","LODHA": "3220","LT": "11483",
    "LTM": "17818","LUPIN": "10440","M&M": "2031","MAHABANK": "11377","MARICO": "4067",
    "MANAPPURAM": "19061","MANKIND": "15380","MARUTI": "10999","MAXHEALTH": "22377",
    "MAZDOCK": "509","MCX": "31181","MFSL": "2142","MOTHERSON": "4204","MPHASIS": "4503",
    "MOTILALOFS": "14947","MUTHOOTFIN": "23650","NAM-INDIA": "357","NATIONALUM": "6364",
    "NAUKRI": "13751","NBCC": "31415","NESTLEIND": "17963","NHPC": "17400","NMDC": "15332",
    "NTPC": "11630","NYKAA": "6545","OBEROIRLTY": "20242","OFSS": "10738","OIL": "17438",
    "ONGC": "2475","PAGEIND": "14413","PATANJALI": "17029","PAYTM": "6705","PERSISTENT": "18365","PETRONET": "11351","PFC": "14299","PGEL": "25358","PHOENIXLTD": "14552",
    "PIDILITIND": "2664","PIIND": "24184","PNB": "10666","PNBHOUSING": "18908",
    "POLICYBZR": "6656","POLYCAB": "9590","POWERGRID": "14977","POWERINDIA": "18457",
    "PREMIERENE": "25049","PRESTIGE": "20302","RADICO": "10990","RBLBANK": "18391",
    "RECLTD": "15355","RELIANCE": "2885","RVNL": "9552","SAGILITY": "27052","SAIL": "2963",
    "SBICARD": "17971","SBILIFE": "21808","SBIN": "3045","SHREECEM": "3103","SRF": "3273",
    "SHRIRAMFIN": "4306","SIEMENS": "3150","SOLARINDS": "13332","SONACOMS": "4684",
    "SUNPHARMA": "3351","SUPREMEIND": "3363","SUZLON": "12018","SWIGGY": "27066",
    "TATACONSUM": "3432","TATAELXSI": "3411","TATAPOWER": "3426","TATASTEEL": "3499",
    "TCS": "11536","TECHM": "13538","TIINDIA": "312","TITAN": "3506","TMPV": "3456",
    "TORNTPHARM": "3518","TRENT": "1964","TVSMOTOR": "8479","UJJIVANSFB": "15228",
    "ULTRACEMCO": "11532","UNIONBANK": "10753","UNITDSPR": "10447","UNOMINDA": "14154",
    "UPL": "11287","VBL": "18921","VEDL": "3063","VMM": "27969","VOLTAS": "3718",
    "WAAREEENER": "25907","WIPRO": "3787","YESBANK": "11915","ZYDUSLIFE": "7929"
    # (এখানে আপনার অরিজিনাল ২১৩টি স্টকের লিস্ট বসিয়ে নেবেন)
}

# Helper Functions (আগের মতোই থাকবে)
def get_headers():
    return {"Content-Type": "application/json", "Accept": "application/json", "access-token": ACCESS_TOKEN, "client-id": CLIENT_ID}

def post_with_retry(url, payload, headers, max_retries=MAX_RETRIES, retry_sleep=5):
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200: return response
            if response.status_code == 429 or response.status_code >= 500: time.sleep(retry_sleep); continue
            return None
        except requests.exceptions.RequestException: time.sleep(retry_sleep)
    return None

def fetch_cash_data(symbol, security_id, trade_date, headers):
    payload = {"securityId": str(security_id), "exchangeSegment": "NSE_EQ", "instrument": "EQUITY", "interval": "5", "oi": False, "fromDate": trade_date, "toDate": trade_date}
    res = post_with_retry(HISTORICAL_URL, payload, headers)
    if not res: return None
    try:
        data = res.json()
        df = pd.DataFrame({"open": data.get("open", []), "high": data.get("high", []), "low": data.get("low", []), "close": data.get("close", []), "volume": data.get("volume", [])}).dropna().apply(pd.to_numeric, errors="coerce").dropna()
        if df.empty: return None
        return {"PDH": float(df["high"].max()), "PDL": float(df["low"].min()), "Closing_Price": float(df["close"].iloc[-1]), "Avg_Volume": float(df["volume"].mean()), "Latest_Volume": float(df["volume"].iloc[-1]), "Volume_Spike_Ratio": 1.0 if float(df["volume"].mean()) <= 0 else (float(df["volume"].iloc[-1]) / float(df["volume"].mean()))}
    except: return None

def fetch_historical_atm_data(symbol, security_id, trade_date_str, headers):
    next_day = (datetime.strptime(trade_date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    def get_opt(opt_type):
        payload = {"exchangeSegment": "NSE_FNO", "interval": "60", "securityId": str(security_id), "instrument": "OPTSTK", "expiryFlag": "MONTH", "expiryCode": 1, "strike": "ATM", "drvOptionType": opt_type, "requiredData": ["iv", "oi", "strike"], "fromDate": trade_date_str, "toDate": next_day}
        res = post_with_retry(ROLLING_OPTION_URL, payload, headers)
        if not res: return None
        try:
            opt = res.json().get("data", {}).get("ce" if opt_type == "CALL" else "pe", {})
            if not opt or not opt.get("iv"): return None
            return {"iv": float(opt["iv"][-1]), "oi": float(opt["oi"][-1]), "strike": float(opt["strike"][-1])}
        except: return None

    ce, pe = get_opt("CALL"), get_opt("PUT")
    if not ce and not pe: return None
    valid_ivs = [d["iv"] for d in [ce, pe] if d and d["iv"] > 0]
    atm_strike = ce["strike"] if ce else (pe["strike"] if pe else 0)
    ce_oi, pe_oi = ce["oi"] if ce else 0, pe["oi"] if pe else 0
    return {"ATM_Strike": atm_strike, "ATM_IV": sum(valid_ivs) / len(valid_ivs) if valid_ivs else np.nan, "Support": atm_strike if pe_oi > ce_oi else (atm_strike * 0.99), "Resistance": atm_strike if ce_oi > pe_oi else (atm_strike * 1.01)}

# ================================================================
# 3. TABS FOR NEW DATA & HISTORY
# ================================================================
tab1, tab2 = st.tabs(["📥 Fetch Today's Data", "📅 View History"])

# ----------------- TAB 1: FETCH NEW DATA -----------------
with tab1:
    st.subheader("Fetch new market data using Dhan API")
    FETCH_DATE = st.date_input("Select Trade Date to Fetch", datetime.now().date())
    FETCH_DATE_STR = FETCH_DATE.strftime("%Y-%m-%d")
    
    if st.button("🚀 Fetch & Save Data"):
        if not ACCESS_TOKEN or not CLIENT_ID:
            st.error("⚠️ সাইডবারে Access Token এবং Client ID দিতে ভুলবেন না!")
        else:
            headers = get_headers()
            results = []
            total_stocks = len(STOCKS)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for counter, (symbol, security_id) in enumerate(STOCKS.items(), start=1):
                status_text.text(f"Fetching data for: {symbol} ({counter}/{total_stocks})...")
                cash = fetch_cash_data(symbol, security_id, FETCH_DATE_STR, headers)
                if not cash: continue
                time.sleep(CASH_API_SLEEP)
                
                option_data = fetch_historical_atm_data(symbol, security_id, FETCH_DATE_STR, headers)
                if not option_data or pd.isna(option_data["ATM_IV"]) or option_data["ATM_IV"] == 0: continue
                
                score = cash["Volume_Spike_Ratio"] * float(option_data["ATM_IV"])
                results.append({"Stock": symbol, "Close": round(cash["Closing_Price"], 2), "Support": round(option_data["Support"], 2), "Resistance": round(option_data["Resistance"], 2), "ATM_Strike": round(option_data["ATM_Strike"], 2), "ATM_IV": round(float(option_data["ATM_IV"]), 4), "Vol_Spike": round(cash["Volume_Spike_Ratio"], 4), "Score": round(score, 4), "Trade_Date": FETCH_DATE_STR})
                progress_bar.progress(counter / total_stocks)
                time.sleep(OPTION_CHAIN_SLEEP)
                
            progress_bar.empty()
            
            if results:
                df = pd.DataFrame(results).sort_values(by="Score", ascending=False).reset_index(drop=True)
                df.insert(0, "Rank", range(1, len(df) + 1))
                
                # সেভ করা হচ্ছে
                save_path = os.path.join(SAVE_DIR, f"Watchlist_{FETCH_DATE_STR}.csv")
                df.to_csv(save_path, index=False)
                status_text.success(f"✅ Data successfully fetched and saved for {FETCH_DATE_STR}!")
                
                st.dataframe(df.head(10), use_container_width=True)
            else:
                status_text.warning("❌ No valid stocks found. Check API limit or Market Holiday.")

# ----------------- TAB 2: VIEW HISTORY -----------------
with tab2:
    st.subheader("View previously saved data (No API needed)")
    HISTORY_DATE = st.date_input("Select a Date to View History", datetime.now().date(), key="history")
    HISTORY_DATE_STR = HISTORY_DATE.strftime("%Y-%m-%d")
    
    file_path = os.path.join(SAVE_DIR, f"Watchlist_{HISTORY_DATE_STR}.csv")
    
    if os.path.exists(file_path):
        st.success(f"📂 Data found for {HISTORY_DATE_STR}")
        history_df = pd.read_csv(file_path)
        st.dataframe(history_df, use_container_width=True)
        
        # Download Option
        csv_data = history_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download this CSV", data=csv_data, file_name=f"Watchlist_{HISTORY_DATE_STR}.csv", mime="text/csv")
    else:
        st.warning(f"⚠️ {HISTORY_DATE_STR} তারিখের কোনো ডেটা সেভ করা নেই। দয়া করে আগে 'Fetch Today's Data' ট্যাব থেকে ডেটা ফেচ করুন।")

