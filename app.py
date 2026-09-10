import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import date, timedelta
import re

st.set_page_config(
    page_title="台股雷達 TW STOCK RADAR",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------- UI ----------
st.markdown("""
<style>
:root{
    --bg:#07111f;
    --card:#0d1b2a;
    --card2:#102235;
    --line:#20364d;
    --text:#f5f7fb;
    --muted:#8ea1b7;
    --green:#23d18b;
    --red:#ff5b63;
    --gold:#f3b84b;
    --blue:#4ea1ff;
}
html,body,[data-testid="stAppViewContainer"]{
    background:
      radial-gradient(circle at 80% 0%, rgba(44,96,160,.14), transparent 28rem),
      linear-gradient(180deg,#07111f 0%,#091421 100%) !important;
    color:var(--text);
}
[data-testid="stHeader"]{
    background:transparent;
}
.block-container{
    max-width:720px;
    padding-top:4.5rem !important;
    padding-bottom:5rem !important;
}
h1,h2,h3,p,span,label,div{
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang TC","Noto Sans TC",sans-serif;
}
h1{font-size:2rem!important;line-height:1.2!important;margin-bottom:.25rem!important}
small,.muted{color:var(--muted)}
[data-testid="stExpander"]{
    background:rgba(13,27,42,.72);
    border:1px solid var(--line);
    border-radius:16px;
    overflow:hidden;
}
[data-testid="stTextInput"] input{
    background:#101d2e!important;
    color:#fff!important;
    border:1px solid #2b425a!important;
    border-radius:14px!important;
    min-height:52px;
}
[data-testid="stTextInput"] input:focus{
    border-color:#4ea1ff!important;
    box-shadow:0 0 0 1px #4ea1ff!important;
}
.stButton>button{
    min-height:52px;
    border-radius:14px;
    font-size:1.02rem;
    font-weight:800;
    border:0;
}
.stButton>button[kind="primary"]{
    background:linear-gradient(135deg,#ff4e57,#ff6b58)!important;
    color:white!important;
    box-shadow:0 10px 30px rgba(255,79,87,.18);
}
[data-testid="stSegmentedControl"]{
    background:transparent!important;
}
[data-testid="stSegmentedControl"] button{
    border-radius:12px!important;
    min-height:44px!important;
    border-color:#294158!important;
}
[data-testid="stSegmentedControl"] button[aria-pressed="true"]{
    border-color:#f3b84b!important;
    box-shadow:0 0 0 1px rgba(243,184,75,.45) inset;
}
.hero{
    border:1px solid var(--line);
    background:linear-gradient(145deg,rgba(15,32,50,.95),rgba(8,20,32,.98));
    border-radius:22px;
    padding:20px;
    margin:14px 0 16px;
    box-shadow:0 18px 45px rgba(0,0,0,.22);
}
.hero-top{
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:12px;
}
.stock-name{
    font-size:1.7rem;
    font-weight:900;
    letter-spacing:.2px;
}
.badge{
    display:inline-block;
    padding:5px 10px;
    border:1px solid #31475e;
    border-radius:999px;
    color:#c9d7e6;
    font-size:.8rem;
    margin-right:5px;
    background:rgba(255,255,255,.025);
}
.price{
    font-size:2.55rem;
    font-weight:950;
    line-height:1;
    margin-top:14px;
}
.change-up{color:var(--red);font-weight:800;margin-top:10px}
.change-down{color:var(--green);font-weight:800;margin-top:10px}
.scorebox{
    min-width:108px;
    border:1px solid #165c43;
    background:linear-gradient(145deg,rgba(11,58,44,.72),rgba(7,31,28,.72));
    border-radius:18px;
    padding:12px 14px;
    text-align:center;
}
.score{
    font-size:2rem;
    font-weight:950;
    color:#50e3a4;
}
.signal-card{
    padding:16px 18px;
    border-radius:18px;
    background:linear-gradient(145deg,#101e2e,#0b1724);
    color:#fff;
    border:1px solid #263b51;
    margin:.8rem 0 1rem;
}
.signal-title{font-size:1.28rem;font-weight:900}
.meta{font-size:.86rem;color:#8ea1b7}
.section-title{
    font-size:1.18rem;
    font-weight:900;
    margin:1.2rem 0 .65rem;
}
.level-grid{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:10px;
    margin:10px 0 6px;
}
.level-card{
    background:linear-gradient(145deg,#0f1d2c,#0a1723);
    border:1px solid #263d55;
    border-radius:18px;
    padding:14px 15px;
    min-height:103px;
}
.level-card.green{border-color:#0b8057;background:linear-gradient(145deg,rgba(10,64,47,.42),rgba(9,26,27,.9))}
.level-card.red{border-color:#9f3f48;background:linear-gradient(145deg,rgba(83,25,32,.42),rgba(22,18,24,.9))}
.level-card.gold{border-color:#9a7124;background:linear-gradient(145deg,rgba(91,62,18,.42),rgba(23,22,20,.9))}
.level-card.blue{border-color:#29659a;background:linear-gradient(145deg,rgba(19,59,91,.42),rgba(10,23,36,.9))}
.level-label{font-size:.86rem;color:#a8b9c9;margin-bottom:7px}
.level-value{font-size:1.42rem;font-weight:950;color:#fff}
.info-grid{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:9px 14px;
    background:#0b1826;
    border:1px solid #22374c;
    border-radius:18px;
    padding:15px 16px;
    margin:10px 0;
}
.info-row{
    display:flex;
    justify-content:space-between;
    gap:10px;
    font-size:.9rem;
    color:#cbd7e4;
}
.info-row b{color:#fff}
.note-card{
    padding:14px 16px;
    border-radius:16px;
    border:1px solid #233b52;
    background:#0a1724;
    color:#c9d5e3;
    margin-top:12px;
}
[data-testid="stMetric"]{
    background:linear-gradient(145deg,#101e2e,#0b1724)!important;
    border:1px solid #263b51!important;
    border-radius:16px!important;
    padding:12px!important;
}
[data-testid="stMetricLabel"]{color:#95a9bd!important}
[data-testid="stMetricValue"]{color:#fff!important}
[data-testid="stMetricDelta"]{color:#a9bacb!important}
[data-testid="stAlert"]{
    border-radius:16px!important;
}
footer{visibility:hidden}
#MainMenu{visibility:hidden}
@media(max-width:520px){
    .block-container{padding-left:1rem!important;padding-right:1rem!important;padding-top:4.25rem!important}
    .hero{padding:17px}
    .stock-name{font-size:1.52rem}
    .price{font-size:2.25rem}
    .scorebox{min-width:96px;padding:10px}
    .score{font-size:1.75rem}
    .level-value{font-size:1.28rem}
}
</style>
""", unsafe_allow_html=True)

API = "https://api.finmindtrade.com/api/v4/data"

# ---------- Data ----------
@st.cache_data(ttl=1800, show_spinner=False)
def fm_get(dataset, data_id=None, start_date=None, end_date=None, token=""):
    params = {"dataset": dataset}
    if data_id:
        params["data_id"] = data_id
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if token:
        params["token"] = token

    r = requests.get(API, params=params, timeout=25)
    r.raise_for_status()
    j = r.json()
    if j.get("status") not in (200, "200"):
        raise RuntimeError(j.get("msg", "FinMind API 錯誤"))
    return pd.DataFrame(j.get("data", []))


@st.cache_data(ttl=21600, show_spinner=False)
def stock_universe(token=""):
    try:
        return fm_get("TaiwanStockInfo", token=token)
    except Exception:
        return pd.DataFrame()


def resolve_security(query, token=""):
    q = str(query).strip().upper().replace(" ", "")
    uni = stock_universe(token)

    if not uni.empty:
        cols = {c.lower(): c for c in uni.columns}
        code_col = cols.get("stock_id") or cols.get("stockid") or cols.get("code")
        name_col = cols.get("stock_name") or cols.get("stockname") or cols.get("name")
        type_col = cols.get("type")
        industry_col = cols.get("industry_category") or cols.get("industry")
        market_col = cols.get("market")

        if code_col and name_col:
            tmp = uni.copy()
            tmp[code_col] = tmp[code_col].astype(str).str.upper()
            exact = tmp[tmp[code_col] == q]
            if exact.empty:
                exact = tmp[
                    tmp[name_col].astype(str).str.contains(
                        re.escape(str(query).strip()), na=False
                    )
                ]
            if not exact.empty:
                row = exact.iloc[0]
                return {
                    "code": str(row[code_col]).upper(),
                    "name": str(row[name_col]),
                    "type": str(row[type_col]) if type_col and pd.notna(row[type_col]) else "",
                    "industry": str(row[industry_col]) if industry_col and pd.notna(row[industry_col]) else "",
                    "market": str(row[market_col]) if market_col and pd.notna(row[market_col]) else "",
                }

    if re.fullmatch(r"[0-9A-Z]{4,8}", q):
        return {"code": q, "name": q, "type": "", "industry": "", "market": ""}

    raise ValueError("找不到此股票代號或中文名稱")


def infer_kind(info):
    text = " ".join(
        [info.get("name", ""), info.get("type", ""), info.get("industry", ""), info.get("market", "")]
    ).lower()
    code = info.get("code", "").upper()
    leveraged = "槓桿" in text or "反向" in text or code.endswith("L") or code.endswith("R")
    etf = "etf" in text or leveraged or code.startswith(("00", "01"))
    return "槓桿／反向 ETF" if leveraged else ("ETF" if etf else "個股")


def infer_market(info):
    text = " ".join([info.get("market", ""), info.get("type", ""), info.get("industry", "")])
    if "上櫃" in text or "OTC" in text.upper():
        return "上櫃"
    if "興櫃" in text:
        return "興櫃"
    if "上市" in text or "TWSE" in text.upper():
        return "上市"
    return info.get("market", "") or "台股"


def fetch_bundle(code, token=""):
    end = date.today()
    sp = (end - timedelta(days=180)).isoformat()
    sc = (end - timedelta(days=50)).isoformat()
    e = end.isoformat()

    price = fm_get("TaiwanStockPrice", code, sp, e, token)
    inst = fm_get("TaiwanStockInstitutionalInvestorsBuySell", code, sc, e, token)
    margin = fm_get("TaiwanStockMarginPurchaseShortSale", code, sc, e, token)
    try:
        daytrade = fm_get("TaiwanStockDayTrading", code, sc, e, token)
    except Exception:
        daytrade = pd.DataFrame()

    return price, inst, margin, daytrade


def normalize_price(df):
    if df.empty:
        raise ValueError("查不到價格資料")

    x = df.copy()
    ren = {}
    for c in x.columns:
        lc = c.lower()
        if lc == "close":
            ren[c] = "close"
        elif lc == "open":
            ren[c] = "open"
        elif lc in ("max", "high"):
            ren[c] = "high"
        elif lc in ("min", "low"):
            ren[c] = "low"
        elif lc in ("trading_volume", "volume"):
            ren[c] = "volume"
        elif lc in ("trading_money", "amount"):
            ren[c] = "amount"

    x = x.rename(columns=ren)
    x["date"] = pd.to_datetime(x["date"], errors="coerce")
    for c in ["open", "high", "low", "close", "volume", "amount"]:
        if c in x.columns:
            x[c] = pd.to_numeric(x[c], errors="coerce")

    x = x.dropna(subset=["date", "close"]).sort_values("date")
    if len(x) < 20:
        raise ValueError("歷史資料不足 20 個交易日")
    return x


def institutional_5d(df):
    out = {"foreign": 0.0, "trust": 0.0, "dealer": 0.0, "total": 0.0}
    if df.empty or not {"date", "name", "buy", "sell"}.issubset(df.columns):
        return out

    x = df.copy()
    x["buy"] = pd.to_numeric(x["buy"], errors="coerce").fillna(0)
    x["sell"] = pd.to_numeric(x["sell"], errors="coerce").fillna(0)
    x["net"] = x["buy"] - x["sell"]
    days = sorted(x["date"].astype(str).unique())[-5:]
    x = x[x["date"].astype(str).isin(days)]

    def sm(names):
        return float(x[x["name"].isin(names)]["net"].sum())

    out["foreign"] = sm(["Foreign_Investor", "Foreign_Dealer_Self"])
    out["trust"] = sm(["Investment_Trust"])
    out["dealer"] = sm(["Dealer_self", "Dealer_Hedging", "Dealer"])
    out["total"] = out["foreign"] + out["trust"] + out["dealer"]
    return out


def margin_5d(df):
    out = {"margin_pct": 0.0, "short_pct": 0.0}
    if df.empty:
        return out

    x = df.copy().sort_values("date")
    m = "MarginPurchaseTodayBalance"
    s = "ShortSaleTodayBalance"

    if m not in x.columns:
        return out

    x[m] = pd.to_numeric(x[m], errors="coerce")
    if s in x.columns:
        x[s] = pd.to_numeric(x[s], errors="coerce")
    x = x.dropna(subset=[m])

    if len(x) < 2:
        return out

    k = min(5, len(x) - 1)
    m0, m1 = float(x.iloc[-k - 1][m]), float(x.iloc[-1][m])
    out["margin_pct"] = (m1 - m0) / max(abs(m0), 1)

    if s in x.columns and pd.notna(x.iloc[-k - 1][s]) and pd.notna(x.iloc[-1][s]):
        s0, s1 = float(x.iloc[-k - 1][s]), float(x.iloc[-1][s])
        out["short_pct"] = (s1 - s0) / max(abs(s0), 1)

    return out


def tick_size(p):
    p = float(p)
    if p < 10:
        return 0.01
    if p < 50:
        return 0.05
    if p < 100:
        return 0.1
    if p < 500:
        return 0.5
    if p < 1000:
        return 1.0
    return 5.0


def tradable(p):
    step = tick_size(p)
    return round(round(float(p) / step) * step, 2)


def indicators(df):
    x = normalize_price(df)

    x["ma5"] = x["close"].rolling(5).mean()
    x["ma10"] = x["close"].rolling(10).mean()
    x["ma20"] = x["close"].rolling(20).mean()

    prev = x["close"].shift(1)
    tr = pd.concat(
        [
            x["high"] - x["low"],
            (x["high"] - prev).abs(),
            (x["low"] - prev).abs(),
        ],
        axis=1,
    ).max(axis=1)
    x["atr14"] = tr.rolling(14).mean()

    if "amount" in x.columns and "volume" in x.columns:
        v = x["amount"] / x["volume"].replace(0, np.nan)
        x["vwap_proxy"] = v.where(
            (v > x["low"] * 0.5) & (v < x["high"] * 1.5),
            (x["high"] + x["low"] + x["close"]) / 3,
        )
    else:
        x["vwap_proxy"] = (x["high"] + x["low"] + x["close"]) / 3

    return x


def score_direction(x, chip, marg, kind):
    last = x.iloc[-1]
    close = float(last["close"])
    score = 50

    score += 9 if close > last["ma20"] else -9

    if last["ma5"] > last["ma10"] > last["ma20"]:
        score += 10
    elif last["ma5"] < last["ma10"] < last["ma20"]:
        score -= 10

    if kind == "個股":
        score += 10 if chip["foreign"] > 0 else -8
        score += 8 if chip["trust"] > 0 else -6
        score += 4 if chip["dealer"] > 0 else -3

        if marg["margin_pct"] > 0.05 and close < last["ma5"]:
            score -= 7
        elif marg["margin_pct"] < -0.03 and close >= last["ma5"]:
            score += 5
    else:
        ret5 = close / x.iloc[-6]["close"] - 1 if len(x) >= 6 else 0
        score += 8 if ret5 > 0 else -8

    score = int(max(0, min(100, score)))
    label = (
        "偏多"
        if score >= 70
        else ("中性偏多" if score >= 55 else ("觀望" if score >= 40 else "偏空"))
    )
    return score, label


def build_levels(price_df, chip, marg, kind, mode):
    x = indicators(price_df)
    last = x.iloc[-1]

    close = float(last["close"])
    atr = float(last["atr14"]) if pd.notna(last["atr14"]) and last["atr14"] > 0 else close * 0.02
    ma5 = float(last["ma5"])
    ma10 = float(last["ma10"])
    ma20 = float(last["ma20"])
    vwap = float(last["vwap_proxy"])

    today_low = float(last["low"])
    today_high = float(last["high"])
    today_open = float(last["open"]) if "open" in last and pd.notna(last["open"]) else np.nan
    today_volume = float(last["volume"]) if "volume" in last and pd.notna(last["volume"]) else np.nan

    prev = x.iloc[-2]
    prev_low = float(prev["low"])
    prev_high = float(prev["high"])

    r5 = x.tail(5)
    r10 = x.tail(10)
    r20 = x.tail(20)

    score, label = score_direction(x, chip, marg, kind)

    first_center = float(
        np.median(
            [
                float(r5["low"].median()),
                float(r10["low"].quantile(0.35)),
                ma5,
                ma10,
                vwap,
                prev_low,
            ]
        )
    )
    first_center = min(first_center, close - 0.03 * atr)

    second_center = float(
        np.median(
            [
                float(r10["low"].quantile(0.15)),
                float(r20["low"].quantile(0.20)),
                ma20,
                float(r20["low"].min()),
            ]
        )
    )
    second_center = min(second_center, first_center - 0.35 * atr)

    if mode == "⚡ 當沖":
        w1, w2, stop_pad, tp1_pad, tp2_pad = 0.12, 0.16, 0.28, 0.45, 0.80
    elif mode == "🌙 隔日":
        w1, w2, stop_pad, tp1_pad, tp2_pad = 0.18, 0.24, 0.42, 0.75, 1.25
    else:
        w1, w2, stop_pad, tp1_pad, tp2_pad = 0.28, 0.38, 0.70, 1.20, 2.00

    if "槓桿" in kind:
        w1 *= 0.9
        w2 *= 0.9
        stop_pad *= 1.05
        tp1_pad *= 1.05
        tp2_pad *= 1.10

    entry1_low = first_center - w1 * atr
    entry1_high = min(first_center + w1 * atr, close - tick_size(close))
    entry2_low = second_center - w2 * atr
    entry2_high = min(second_center + w2 * atr, entry1_low - tick_size(close))

    structure_low = min(
        prev_low,
        today_low,
        float(r10["low"].min()),
        float(r20["low"].quantile(0.10)),
    )
    stop = min(entry2_low - stop_pad * atr, structure_low - 0.08 * atr)

    resistances = [
        prev_high,
        today_high,
        float(r5["high"].max()),
        float(r10["high"].quantile(0.75)),
        float(r20["high"].quantile(0.85)),
    ]
    above = [r for r in resistances if r > close]
    first_res = min(above) if above else close + tp1_pad * atr

    tp1 = max(first_res, close + tp1_pad * atr)
    tp2 = max(float(r20["high"].max()), tp1 + 0.55 * atr, close + tp2_pad * atr)
    breakout = max(prev_high, today_high, float(r5["high"].max()), first_res) + 0.05 * atr
    nochase = breakout + 0.30 * atr

    e1l, e1h = tradable(entry1_low), tradable(entry1_high)
    e2l, e2h = tradable(entry2_low), tradable(entry2_high)
    stp = tradable(stop)
    t1p = tradable(tp1)
    t2p = tradable(tp2)
    br = tradable(breakout)
    nc = tradable(nochase)

    if e1l > e1h:
        e1l = tradable(e1h - max(0.18 * atr, tick_size(e1h)))
    if e2h >= e1l:
        e2h = tradable(e1l - tick_size(e1l))
    if e2l > e2h:
        e2l = tradable(e2h - max(0.22 * atr, tick_size(e2h)))
    if stp >= e2l:
        stp = tradable(e2l - max(0.35 * atr, tick_size(e2l)))
    if t1p <= e1h:
        t1p = tradable(e1h + max(0.45 * atr, tick_size(e1h)))
    if t2p <= t1p:
        t2p = tradable(t1p + max(0.60 * atr, tick_size(t1p)))
    if br <= close:
        br = tradable(close + max(0.15 * atr, tick_size(close)))
    if nc <= br:
        nc = tradable(br + max(0.25 * atr, tick_size(br)))

    em = (e1l + e1h) / 2
    risk = max(em - stp, tick_size(close))
    reward = max(t1p - em, tick_size(close))

    return {
        "x": x,
        "close": close,
        "atr": atr,
        "vwap": vwap,
        "score": score,
        "label": label,
        "entry1": f"{e1l:g}～{e1h:g}",
        "entry2": f"{e2l:g}～{e2h:g}",
        "stop": f"{stp:g}",
        "tp1": f"{t1p:g}",
        "tp2": f"{t2p:g}",
        "breakout": f"{br:g}",
        "nochase": f"{nc:g}",
        "rr": reward / risk,
        "today_open": today_open,
        "today_low": today_low,
        "today_high": today_high,
        "today_volume": today_volume,
        "prev_low": prev_low,
        "prev_high": prev_high,
        "ma5": ma5,
        "ma10": ma10,
        "ma20": ma20,
    }


def fmt_volume(v):
    if pd.isna(v):
        return "—"
    return f"{v/1000:,.0f} 張"


def chip_color(v):
    return "🔴" if v > 0 else ("🟢" if v < 0 else "⚪")


# ---------- App ----------
st.markdown("# 📊 台股雷達")
st.caption("TW STOCK RADAR｜上市・上櫃・ETF・槓桿ETF")

with st.expander("⚙️ API 設定（可選）"):
    token = st.text_input(
        "FinMind Token",
        type="password",
        help="可以先不填。遇到 FinMind API 流量限制時再填。",
    )

query = st.text_input(
    "搜尋股票代號或中文名稱",
    value="2330",
    placeholder="例如：2330、4707、00631L、台積電",
)

mode = st.segmented_control(
    "分析模式",
    ["⚡ 當沖", "🌙 隔日", "📈 波段"],
    default="⚡ 當沖",
)

go = st.button("🔎 搜尋並分析", use_container_width=True, type="primary")

if go:
    try:
        with st.spinner("正在抓取市場與籌碼資料…"):
            info = resolve_security(query, token)
            code = info["code"]

            price, inst, margin, daytrade = fetch_bundle(code, token)
            kind = infer_kind(info)
            market = infer_market(info)
            chip = institutional_5d(inst)
            marg = margin_5d(margin)
            lv = build_levels(price, chip, marg, kind, mode)

            x = lv["x"]
            last = x.iloc[-1]
            prev_close = float(x.iloc[-2]["close"])
            change = lv["close"] - prev_close
            pct = change / prev_close * 100 if prev_close else 0

        change_class = "change-up" if change >= 0 else "change-down"
        arrow = "▲" if change >= 0 else "▼"

        st.markdown(
            f"""
            <div class="hero">
              <div class="hero-top">
                <div>
                  <div class="stock-name">{code}｜{info['name']}</div>
                  <div style="margin-top:8px">
                    <span class="badge">{market}</span>
                    <span class="badge">{kind}</span>
                    <span class="badge">資料日 {last['date'].date()}</span>
                  </div>
                  <div class="price">{lv['close']:g} 元</div>
                  <div class="{change_class}">{arrow} {change:+.2f}（{pct:+.2f}%）</div>
                </div>
                <div class="scorebox">
                  <div class="meta">綜合評分</div>
                  <div class="score">{lv['score']}</div>
                  <div style="font-weight:900">{lv['label']}</div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="signal-card">
              <div class="signal-title">{mode}｜{lv['label']}</div>
              <div class="meta" style="margin-top:6px">
                風險報酬比 1 : {lv['rr']:.2f} ・ ATR14 {lv['atr']:.2f}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-title">🎯 交易價位</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="level-grid">
              <div class="level-card green">
                <div class="level-label">🟢 第一進場</div>
                <div class="level-value">{lv['entry1']}</div>
              </div>
              <div class="level-card green">
                <div class="level-label">🟢 第二進場</div>
                <div class="level-value">{lv['entry2']}</div>
              </div>
              <div class="level-card red">
                <div class="level-label">🛑 停損</div>
                <div class="level-value">{lv['stop']}</div>
              </div>
              <div class="level-card gold">
                <div class="level-label">🎯 第一停利 TP1</div>
                <div class="level-value">{lv['tp1']}</div>
              </div>
              <div class="level-card gold">
                <div class="level-label">🎯 第二停利 TP2</div>
                <div class="level-value">{lv['tp2']}</div>
              </div>
              <div class="level-card blue">
                <div class="level-label">🚀 突破確認</div>
                <div class="level-value">{lv['breakout']}</div>
              </div>
              <div class="level-card red">
                <div class="level-label">⚠️ 不追價</div>
                <div class="level-value">{lv['nochase']}</div>
              </div>
              <div class="level-card blue">
                <div class="level-label">⚖️ 風險報酬</div>
                <div class="level-value">1 : {lv['rr']:.2f}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if lv["label"] == "偏空":
            st.warning("目前偏空：進場區只作為支撐觀察，不代表建議接刀。")
        elif lv["label"] == "觀望":
            st.info("目前中性：價格到進場區後，再觀察量價承接與大盤方向。")

        st.markdown('<div class="section-title">📈 近期趨勢</div>', unsafe_allow_html=True)
        chart_df = x.tail(40)[["date", "close"]].copy().set_index("date")
        st.line_chart(chart_df, height=210, use_container_width=True)

        st.markdown('<div class="section-title">📌 關鍵資料</div>', unsafe_allow_html=True)

        open_text = "—" if pd.isna(lv["today_open"]) else f"{lv['today_open']:g}"
        volume_text = fmt_volume(lv["today_volume"])

        st.markdown(
            f"""
            <div class="info-grid">
              <div class="info-row"><span>開盤</span><b>{open_text}</b></div>
              <div class="info-row"><span>最高</span><b>{lv['today_high']:g}</b></div>
              <div class="info-row"><span>最低</span><b>{lv['today_low']:g}</b></div>
              <div class="info-row"><span>昨高</span><b>{lv['prev_high']:g}</b></div>
              <div class="info-row"><span>昨低</span><b>{lv['prev_low']:g}</b></div>
              <div class="info-row"><span>成交量</span><b>{volume_text}</b></div>
              <div class="info-row"><span>MA5</span><b>{lv['ma5']:.2f}</b></div>
              <div class="info-row"><span>MA20</span><b>{lv['ma20']:.2f}</b></div>
              <div class="info-row"><span>VWAP 近似</span><b>{lv['vwap']:.2f}</b></div>
              <div class="info-row"><span>ATR14</span><b>{lv['atr']:.2f}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-title">💰 籌碼資訊</div>', unsafe_allow_html=True)

        if kind == "個股":
            c1, c2, c3 = st.columns(3)
            c1.metric("外資 5 日", f"{chip['foreign']/1000:,.0f} 張")
            c2.metric("投信 5 日", f"{chip['trust']/1000:,.0f} 張")
            c3.metric("自營商 5 日", f"{chip['dealer']/1000:,.0f} 張")

            c1, c2 = st.columns(2)
            c1.metric("融資 5 日", f"{marg['margin_pct']*100:+.2f}%")
            c2.metric("融券 5 日", f"{marg['short_pct']*100:+.2f}%")
        else:
            st.info("ETF／槓桿 ETF 主要以價格趨勢、波動與支撐壓力分析，不直接套用一般個股法人權重。")

        st.markdown('<div class="section-title">💡 今日觀察重點</div>', unsafe_allow_html=True)

        obs = []
        if lv["close"] > lv["ma20"]:
            obs.append("股價位於 MA20 之上，中期結構相對偏強。")
        else:
            obs.append("股價位於 MA20 之下，中期結構仍需保守。")

        if kind == "個股":
            if chip["foreign"] > 0:
                obs.append("外資近 5 日為買超，籌碼面有正向支撐。")
            else:
                obs.append("外資近 5 日未呈現買超，追價時需留意籌碼壓力。")

        obs.append(f"突破確認價為 {lv['breakout']}；高於 {lv['nochase']} 則列為不追價區。")

        st.markdown(
            "<div class='note-card'>" +
            "<br>".join([f"{i+1}. {t}" for i, t in enumerate(obs)]) +
            "</div>",
            unsafe_allow_html=True,
        )

        with st.expander("查看完整技術依據"):
            st.write(f"MA5：{lv['ma5']:.2f}")
            st.write(f"MA10：{lv['ma10']:.2f}")
            st.write(f"MA20：{lv['ma20']:.2f}")
            st.write(f"ATR14：{lv['atr']:.2f}")
            st.write(f"VWAP 近似值：{lv['vwap']:.2f}")
            st.caption("價位區間依近期高低、均線、ATR、昨高昨低與 VWAP 近似值建立，不使用單純固定百分比。")

        st.markdown(
            "<div class='note-card'>"
            "⚠️ 本工具僅供交易規劃與資料分析。FinMind 免費資料可能延遲，實際下單前請以券商即時行情確認。"
            "</div>",
            unsafe_allow_html=True,
        )

    except Exception as e:
        st.error(f"查詢失敗：{e}")
        st.caption("若遇到 FinMind API 流量限制，可在上方 API 設定填入 FinMind Token。")
