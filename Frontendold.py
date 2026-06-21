import streamlit as st
import requests
import pandas as pd
import time

from configold import COMBINED_API_URL

# ==============================================================
# CONFIG
# ==============================================================

API = COMBINED_API_URL          # e.g. http://74.208.190.247:8000
USERNAME         = "OrivisAlpha"
PASSWORD         = "Orivis"
REFRESH_INTERVAL = 300          # 5 minutes

# ==============================================================
# PAGE CONFIG
# ==============================================================

st.set_page_config(
    page_title="Orivis Alpha – Combined Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================
# LOGIN
# ==============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("🔐 Orivis Alpha Login")
    user = st.text_input("Username")
    pwd  = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == USERNAME and pwd == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.authenticated:
    login()
    st.stop()

# ==============================================================
# SIDEBAR NAVIGATION
# ==============================================================

st.sidebar.image("https://i.imgur.com/placeholder.png", use_column_width=True) if False else None

st.sidebar.title("📊 Orivis Alpha")
st.sidebar.markdown("---")

TAB = st.sidebar.radio(
    "Select Indicator",
    [
        "Fib – Gen",
        "Fib – JPY",
        "RSI – Gen",
        "RSI – JPY",
        "Bollinger – Gen",
        "Bollinger – JPY",
        "MA – Gen",
        "MA – JPY",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Auto-refreshes every {REFRESH_INTERVAL // 60} min")

# ==============================================================
# HELPERS
# ==============================================================

def get(path):
    try:
        r = requests.get(f"{API}{path}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
    return None


def show_ts(ts):
    if ts:
        st.caption(f"🕒 Last updated: {ts}")


# ==============================================================
# TAB: FIB GEN
# ==============================================================

def tab_fib_gen():
    st.header("Fibonacci Signals – Gen Pairs")
    data = get("/fib-gen/signal")
    if not data:
        st.warning("No data from API"); return
    show_ts(data.get("timestamp"))
    table = data.get("table", [])
    if not table:
        st.info("Engine warming up…"); return
    df = pd.DataFrame(table)
    rename_dict = {}
    if "TrendDirection" in df.columns:
        rename_dict["TrendDirection"] = "Trend Direction"
    if "trade_direction" in df.columns:
        rename_dict["trade_direction"] = "Trade Direction"
    if rename_dict:
        df = df.rename(columns=rename_dict)
    cols = ["Symbol", "Timeframe"] + [c for c in df.columns if c not in ("Symbol", "Timeframe")]
    st.dataframe(df[cols], use_container_width=True, hide_index=True)


# ==============================================================
# TAB: FIB JPY
# ==============================================================

def tab_fib_jpy():
    st.header("Fibonacci Signals – JPY Pairs")
    data = get("/fib-jpy/signal")
    if not data:
        st.warning("No data from API"); return
    show_ts(data.get("timestamp"))
    table = data.get("table", [])
    if not table:
        st.info("Engine warming up…"); return
    df = pd.DataFrame(table)
    rename_dict = {}
    if "TrendDirection" in df.columns:
        rename_dict["TrendDirection"] = "Trend Direction"
    if "trade_direction" in df.columns:
        rename_dict["trade_direction"] = "Trade Direction"
    if rename_dict:
        df = df.rename(columns=rename_dict)
    cols = ["Symbol", "Timeframe"] + [c for c in df.columns if c not in ("Symbol", "Timeframe")]
    st.dataframe(df[cols], use_container_width=True, hide_index=True)


# ==============================================================
# TAB: RSI GEN
# ==============================================================

def tab_rsi(prefix, title):
    st.header(f"RSI – {title}")
    rsi_data  = get(f"/{prefix}/rsi")
    obos_data = get(f"/{prefix}/rsi-ob-os")
    if not rsi_data or not obos_data:
        st.warning("No data from API"); return
    show_ts(str(rsi_data.get("timestamp", "")))
    df_rsi  = pd.DataFrame(rsi_data.get("data", []))
    if df_rsi.empty:
        st.info("Engine warming up…"); return
    # df_rsi already contains 'ob_os' from the backend — merging with df_obos
    # creates duplicate columns (ob_os_x / ob_os_y) that break the rename below.
    # Use df_rsi directly; fall back to df_obos only if ob_os is somehow missing.
    if "ob_os" not in df_rsi.columns:
        df_obos = pd.DataFrame(obos_data.get("data", []))
        if not df_obos.empty:
            df_rsi = pd.merge(
                df_rsi,
                df_obos[["symbol", "timeframe", "ob_os"]],
                on=["symbol", "timeframe"],
                how="left",
            )
    df = df_rsi.copy()
    df.drop(columns=[c for c in ["Adjusted_RSI"] if c in df.columns], inplace=True)
    df = df.rename(columns={"symbol": "Symbol", "timeframe": "Timeframe", "ob_os": "Overbought/Oversold"})
    keep = [c for c in ["Symbol", "Timeframe", "RSI", "Overbought/Oversold"] if c in df.columns]
    st.dataframe(df[keep], use_container_width=True, hide_index=True)


# ==============================================================
# TAB: BOLLINGER
# ==============================================================

def tab_bollinger(prefix, title):
    st.header(f"Bollinger Volatility – {title}")
    data = get(f"/{prefix}/bollinger")
    if not data:
        st.warning("No data from API"); return
    show_ts(data.get("timestamp"))
    rows = []
    for symbol, timeframes in data.get("data", {}).items():
        for tf, vals in timeframes.items():
            rows.append({
                "Symbol":        symbol.replace("m", ""),
                "Timeframe":     tf,
                "Timestamp":     vals["LastClosedTime"],
                "Current Range": vals["CurrentRange"],
                "Max Range":     vals["MaxRange"],
                "Min Range":     vals["MinRange"],
            })
    if not rows:
        st.info("Engine warming up…"); return
    df = pd.DataFrame(rows).sort_values(["Symbol", "Timeframe"])
    st.dataframe(df, use_container_width=True, hide_index=True)


# ==============================================================
# TAB: MA
# ==============================================================

def tab_ma(prefix, title):
    st.header(f"Moving Average Signals – {title}")
    data = get(f"/{prefix}/signals")
    if not data:
        st.warning("No data from API"); return
    rows = data.get("data", [])
    if not rows:
        st.info("Engine warming up…"); return
    df = pd.DataFrame(rows)
    if "Symbol" in df.columns:
        df["Symbol"] = df["Symbol"].str.replace("m", "", regex=False)

    # Support both old backend (SMA50/100/200) and new backend (SMA50_Signal/...)
    col_map = {}
    for short, full in [("SMA50", "SMA50_Signal"), ("SMA100", "SMA100_Signal"), ("SMA200", "SMA200_Signal")]:
        if full in df.columns:
            col_map[full] = f"vs {short}"
        elif short in df.columns:
            col_map[short] = f"vs {short}"

    # Replace any numeric 0 with "NA" for clarity
    for col in col_map:
        df[col] = df[col].apply(lambda v: "NA" if v == 0 else v)

    keep = ["Symbol", "Timeframe"] + list(col_map.keys())
    keep = [c for c in keep if c in df.columns]
    df = df[keep].rename(columns=col_map).sort_values(["Symbol", "Timeframe"])
    st.dataframe(df, use_container_width=True, hide_index=True)


# ==============================================================
# RENDER SELECTED TAB
# ==============================================================

if TAB == "Fib – Gen":
    tab_fib_gen()
elif TAB == "Fib – JPY":
    tab_fib_jpy()
elif TAB == "RSI – Gen":
    tab_rsi("rsi-gen", "Gen Pairs")
elif TAB == "RSI – JPY":
    tab_rsi("rsi-jpy", "JPY Pairs")
elif TAB == "Bollinger – Gen":
    tab_bollinger("bollinger-gen", "Gen Pairs")
elif TAB == "Bollinger – JPY":
    tab_bollinger("bollinger-jpy", "JPY Pairs")
elif TAB == "MA – Gen":
    tab_ma("ma-gen", "Gen Pairs")
elif TAB == "MA – JPY":
    tab_ma("ma-jpy", "JPY Pairs")

# ==============================================================
# AUTO-REFRESH
# ==============================================================

time.sleep(REFRESH_INTERVAL)
st.rerun()
