
import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import date, timedelta
import re

st.set_page_config(page_title="台股籌碼實戰雷達 V2", page_icon="📈", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.block-container{max-width:560px;padding-top:1rem;padding-bottom:3rem}
h1{font-size:1.8rem!important;margin-bottom:.15rem!important}
div[data-testid="stMetric"]{background:#161b22;border:1px solid #30363d;border-radius:15px;padding:12px;color:#ffffff}
.stButton>button{height:48px;border-radius:13px;font-size:1rem;font-weight:700}
div[data-testid="stMetric"] [data-testid="stMetricLabel"]{color:#c9d1d9!important}
div[data-testid="stMetric"] [data-testid="stMetricValue"]{color:#ffffff!important}
div[data-testid="stMetric"] [data-testid="stMetricDelta"]{color:#c9d1d9!important}
.signal-card{padding:16px;border-radius:16px;background:#161b22;color:#ffffff;border:1px solid #30363d;margin:.8rem 0}
.signal-title{font-size:1.25rem;font-weight:800}
.meta{font-size:.85rem;color:#7a7f88}
.price-title{font-size:2rem;font-weight:850;margin:.4rem 0}
.section{font-size:1.2rem;font-weight:800;margin-top:1.3rem}
</style>
""", unsafe_allow_html=True)

API = "https://api.finmindtrade.com/api/v4/data"

@st.cache_data(ttl=1800, show_spinner=False)
def fm_get(dataset, data_id=None, start_date=None, end_date=None, token=""):
    params={"dataset":dataset}
    if data_id: params["data_id"]=data_id
    if start_date: params["start_date"]=start_date
    if end_date: params["end_date"]=end_date
    if token: params["token"]=token
    r=requests.get(API,params=params,timeout=25)
    r.raise_for_status()
    j=r.json()
    if j.get("status") not in (200,"200"): raise RuntimeError(j.get("msg","FinMind API 錯誤"))
    return pd.DataFrame(j.get("data",[]))

@st.cache_data(ttl=21600, show_spinner=False)
def stock_universe(token=""):
    try:
        df=fm_get("TaiwanStockInfo",token=token)
        return df
    except Exception:
        return pd.DataFrame()

def resolve_security(query, token=""):
    q=str(query).strip().upper().replace(" ","")
    uni=stock_universe(token)
    if not uni.empty:
        cols={c.lower():c for c in uni.columns}
        code_col=cols.get("stock_id") or cols.get("stockid") or cols.get("code")
        name_col=cols.get("stock_name") or cols.get("stockname") or cols.get("name")
        type_col=cols.get("type")
        industry_col=cols.get("industry_category") or cols.get("industry")
        market_col=cols.get("market")
        if code_col and name_col:
            tmp=uni.copy()
            tmp[code_col]=tmp[code_col].astype(str).str.upper()
            exact=tmp[tmp[code_col]==q]
            if exact.empty:
                exact=tmp[tmp[name_col].astype(str).str.contains(re.escape(str(query).strip()),na=False)]
            if not exact.empty:
                row=exact.iloc[0]
                return {
                    "code":str(row[code_col]).upper(),
                    "name":str(row[name_col]),
                    "type":str(row[type_col]) if type_col and pd.notna(row[type_col]) else "",
                    "industry":str(row[industry_col]) if industry_col and pd.notna(row[industry_col]) else "",
                    "market":str(row[market_col]) if market_col and pd.notna(row[market_col]) else "",
                }
    if re.fullmatch(r"[0-9A-Z]{4,8}",q):
        return {"code":q,"name":q,"type":"","industry":"","market":""}
    raise ValueError("找不到此股票代號或中文名稱")

def infer_kind(info):
    text=" ".join([info.get("name",""),info.get("type",""),info.get("industry",""),info.get("market","")]).lower()
    code=info.get("code","").upper()
    leveraged=("槓桿" in text or "反向" in text or code.endswith("L") or code.endswith("R"))
    etf=("etf" in text or leveraged or code.startswith(("00","01")))
    return "槓桿／反向 ETF" if leveraged else ("ETF" if etf else "個股")

def infer_market(info):
    text=" ".join([info.get("market",""),info.get("type",""),info.get("industry","")])
    if "上櫃" in text or "OTC" in text.upper(): return "上櫃"
    if "興櫃" in text: return "興櫃"
    if "上市" in text or "TWSE" in text.upper(): return "上市"
    return info.get("market","") or "台股"

def fetch_bundle(code, token=""):
    end=date.today()
    sp=(end-timedelta(days=180)).isoformat()
    sc=(end-timedelta(days=50)).isoformat()
    e=end.isoformat()
    price=fm_get("TaiwanStockPrice",code,sp,e,token)
    inst=fm_get("TaiwanStockInstitutionalInvestorsBuySell",code,sc,e,token)
    margin=fm_get("TaiwanStockMarginPurchaseShortSale",code,sc,e,token)
    try: daytrade=fm_get("TaiwanStockDayTrading",code,sc,e,token)
    except Exception: daytrade=pd.DataFrame()
    return price,inst,margin,daytrade

def normalize_price(df):
    if df.empty: raise ValueError("查不到價格資料")
    x=df.copy()
    ren={}
    for c in x.columns:
        lc=c.lower()
        if lc=="close": ren[c]="close"
        elif lc=="open": ren[c]="open"
        elif lc in ("max","high"): ren[c]="high"
        elif lc in ("min","low"): ren[c]="low"
        elif lc in ("trading_volume","volume"): ren[c]="volume"
        elif lc in ("trading_money","amount"): ren[c]="amount"
    x=x.rename(columns=ren)
    x["date"]=pd.to_datetime(x["date"],errors="coerce")
    for c in ["open","high","low","close","volume","amount"]:
        if c in x.columns: x[c]=pd.to_numeric(x[c],errors="coerce")
    x=x.dropna(subset=["date","close"]).sort_values("date")
    if len(x)<20: raise ValueError("歷史資料不足 20 個交易日")
    return x

def institutional_5d(df):
    out={"foreign":0.0,"trust":0.0,"dealer":0.0,"total":0.0}
    if df.empty or not {"date","name","buy","sell"}.issubset(df.columns): return out
    x=df.copy()
    x["buy"]=pd.to_numeric(x["buy"],errors="coerce").fillna(0)
    x["sell"]=pd.to_numeric(x["sell"],errors="coerce").fillna(0)
    x["net"]=x["buy"]-x["sell"]
    days=sorted(x["date"].astype(str).unique())[-5:]
    x=x[x["date"].astype(str).isin(days)]
    def sm(names): return float(x[x["name"].isin(names)]["net"].sum())
    out["foreign"]=sm(["Foreign_Investor","Foreign_Dealer_Self"])
    out["trust"]=sm(["Investment_Trust"])
    out["dealer"]=sm(["Dealer_self","Dealer_Hedging","Dealer"])
    out["total"]=out["foreign"]+out["trust"]+out["dealer"]
    return out

def margin_5d(df):
    out={"margin_pct":0.0,"short_pct":0.0}
    if df.empty: return out
    x=df.copy().sort_values("date")
    m="MarginPurchaseTodayBalance"; s="ShortSaleTodayBalance"
    if m not in x.columns: return out
    x[m]=pd.to_numeric(x[m],errors="coerce")
    if s in x.columns: x[s]=pd.to_numeric(x[s],errors="coerce")
    x=x.dropna(subset=[m])
    if len(x)<2: return out
    k=min(5,len(x)-1)
    m0,m1=float(x.iloc[-k-1][m]),float(x.iloc[-1][m])
    out["margin_pct"]=(m1-m0)/max(abs(m0),1)
    if s in x.columns and pd.notna(x.iloc[-k-1][s]) and pd.notna(x.iloc[-1][s]):
        s0,s1=float(x.iloc[-k-1][s]),float(x.iloc[-1][s])
        out["short_pct"]=(s1-s0)/max(abs(s0),1)
    return out

def tick_size(p):
    p=float(p)
    if p<10:return 0.01
    if p<50:return 0.05
    if p<100:return 0.1
    if p<500:return 0.5
    if p<1000:return 1.0
    return 5.0

def tradable(p):
    step=tick_size(p)
    return round(round(float(p)/step)*step,2)

def indicators(df):
    x=normalize_price(df)
    x["ma5"]=x["close"].rolling(5).mean()
    x["ma10"]=x["close"].rolling(10).mean()
    x["ma20"]=x["close"].rolling(20).mean()
    prev=x["close"].shift(1)
    tr=pd.concat([x["high"]-x["low"],(x["high"]-prev).abs(),(x["low"]-prev).abs()],axis=1).max(axis=1)
    x["atr14"]=tr.rolling(14).mean()
    if "amount" in x.columns and "volume" in x.columns:
        v=x["amount"]/x["volume"].replace(0,np.nan)
        x["vwap_proxy"]=v.where((v>x["low"]*.5)&(v<x["high"]*1.5),(x["high"]+x["low"]+x["close"])/3)
    else:
        x["vwap_proxy"]=(x["high"]+x["low"]+x["close"])/3
    return x

def score_direction(x,chip,marg,kind):
    last=x.iloc[-1]; close=float(last["close"]); score=50
    score += 9 if close>last["ma20"] else -9
    if last["ma5"]>last["ma10"]>last["ma20"]: score+=10
    elif last["ma5"]<last["ma10"]<last["ma20"]: score-=10
    if kind=="個股":
        score += 10 if chip["foreign"]>0 else -8
        score += 8 if chip["trust"]>0 else -6
        score += 4 if chip["dealer"]>0 else -3
        if marg["margin_pct"]>.05 and close<last["ma5"]: score-=7
        elif marg["margin_pct"]<-.03 and close>=last["ma5"]: score+=5
    else:
        ret5=close/x.iloc[-6]["close"]-1 if len(x)>=6 else 0
        score += 8 if ret5>0 else -8
    score=int(max(0,min(100,score)))
    label="偏多" if score>=70 else ("中性偏多" if score>=55 else ("觀望" if score>=40 else "偏空"))
    return score,label

def build_levels(price_df,chip,marg,kind,mode):
    x=indicators(price_df); last=x.iloc[-1]; close=float(last["close"])
    atr=float(last["atr14"]) if pd.notna(last["atr14"]) and last["atr14"]>0 else close*.02
    ma10=float(last["ma10"]); ma20=float(last["ma20"]); vwap=float(last["vwap_proxy"])
    today_low=float(last["low"]); today_high=float(last["high"])
    prev=x.iloc[-2]; prev_low=float(prev["low"]); prev_high=float(prev["high"])
    r10=x.tail(10); r20=x.tail(20)
    support=min(float(np.median([float(r10["low"].quantile(.25)),ma10,ma20,vwap,prev_low])),close-.05*atr)
    res=[float(r10["high"].quantile(.75)),float(r20["high"].max()),prev_high,today_high]
    score,label=score_direction(x,chip,marg,kind)
    if mode=="⚡ 當沖": e,s,t1,t2=.18,.38,.55,.95
    elif mode=="🌙 隔日": e,s,t1,t2=.28,.55,.9,1.45
    else: e,s,t1,t2=.45,.9,1.4,2.4
    if "槓桿" in kind: e*=.9; s*=1.05; t1*=1.05; t2*=1.1
    entry_low=support-e*atr
    entry_high=min(close,support+.15*atr)
    structural_low=min(prev_low,today_low,float(r10["low"].min()))
    stop=min(entry_low-s*atr,structural_low-.08*atr)
    nearest=min([r for r in res if r>close] or [close+t1*atr])
    tp1=max(close+t1*atr,nearest)
    tp2=max(tp1+.55*atr,close+t2*atr)
    breakout=max(prev_high,today_high,nearest)+.08*atr
    nochase=breakout+.35*atr
    el,eh=tradable(entry_low),tradable(entry_high)
    if eh>=close: eh=tradable(close-tick_size(close))
    if el>eh: el=tradable(eh-max(.2*atr,tick_size(eh)))
    stp=tradable(stop)
    if stp>=el: stp=tradable(el-max(.35*atr,tick_size(el)))
    t1p=tradable(tp1)
    if t1p<=eh: t1p=tradable(eh+max(.5*atr,tick_size(eh)))
    t2p=tradable(tp2)
    if t2p<=t1p: t2p=tradable(t1p+max(.6*atr,tick_size(t1p)))
    br=tradable(breakout); nc=tradable(max(nochase,br+tick_size(br)))
    risk=max(((el+eh)/2)-stp,tick_size(close)); reward=max(t1p-((el+eh)/2),tick_size(close))
    return {"x":x,"close":close,"atr":atr,"vwap":vwap,"score":score,"label":label,
            "entry":f"{el:g}～{eh:g}","stop":f"{stp:g}","tp1":f"{t1p:g}","tp2":f"{t2p:g}",
            "breakout":f"{br:g}","nochase":f"{nc:g}","rr":reward/risk,
            "today_low":today_low,"today_high":today_high,"prev_low":prev_low,"prev_high":prev_high,
            "ma5":float(last["ma5"]),"ma10":ma10,"ma20":ma20}

st.title("📈 台股籌碼實戰雷達 V2")
st.caption("上市・上櫃・ETF・槓桿ETF｜當沖・隔日・波段")

with st.expander("API 設定（可選）"):
    token=st.text_input("FinMind Token",type="password",help="可先不填；若遇到 API 流量限制再填。")

query=st.text_input("搜尋股票代號或中文名稱",value="2330",placeholder="例如：2330、4707、00631L、台積電")
mode=st.segmented_control("分析模式",["⚡ 當沖","🌙 隔日","📈 波段"],default="⚡ 當沖")
go=st.button("🔎 搜尋並分析",use_container_width=True,type="primary")

if go:
    try:
        with st.spinner("正在抓取市場與籌碼資料…"):
            info=resolve_security(query,token); code=info["code"]
            price,inst,margin,daytrade=fetch_bundle(code,token)
            kind=infer_kind(info); market=infer_market(info)
            chip=institutional_5d(inst); marg=margin_5d(margin)
            lv=build_levels(price,chip,marg,kind,mode)
            x=lv["x"]; last=x.iloc[-1]; prev_close=float(x.iloc[-2]["close"])
            change=lv["close"]-prev_close; pct=change/prev_close*100 if prev_close else 0

        st.markdown(f"### {code}｜{info['name']}")
        st.markdown(f"<div class='meta'>{market}・{kind}｜資料日 {last['date'].date()}</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='price-title'>{lv['close']:g} 元</div>",unsafe_allow_html=True)
        st.write(f"{'▲' if change>=0 else '▼'} {change:+.2f}（{pct:+.2f}%）")
        st.markdown(f"<div class='signal-card'><div class='signal-title'>{mode}：{lv['label']}</div><div>評分 {lv['score']} / 100｜風險報酬比 1 : {lv['rr']:.2f}</div></div>",unsafe_allow_html=True)

        a,b=st.columns(2)
        a.metric("🟢 低接／進場區",lv["entry"]); b.metric("🛑 停損價",lv["stop"])
        a.metric("🎯 第一停利",lv["tp1"]); b.metric("🎯 第二停利",lv["tp2"])
        a.metric("🚀 突破確認",lv["breakout"]); b.metric("⚠️ 不追價",lv["nochase"])

        if lv["label"]=="偏空": st.warning("目前偏空：進場區只作為支撐觀察，不代表建議接刀。")
        elif lv["label"]=="觀望": st.info("目前中性，價格到進場區後再觀察量價承接。")

        if mode=="⚡ 當沖":
            c1,c2=st.columns(2)
            c1.metric("今日低點",f"{lv['today_low']:g}"); c2.metric("今日高點",f"{lv['today_high']:g}")
            c1.metric("昨低",f"{lv['prev_low']:g}"); c2.metric("昨高",f"{lv['prev_high']:g}")
            c1.metric("VWAP 近似值",f"{lv['vwap']:.2f}")

        st.markdown("### 📊 籌碼面")
        if kind=="個股":
            c1,c2,c3=st.columns(3)
            c1.metric("外資5日",f"{chip['foreign']/1000:,.0f}張")
            c2.metric("投信5日",f"{chip['trust']/1000:,.0f}張")
            c3.metric("自營5日",f"{chip['dealer']/1000:,.0f}張")
            c1,c2=st.columns(2)
            c1.metric("融資5日",f"{marg['margin_pct']*100:+.2f}%")
            c2.metric("融券5日",f"{marg['short_pct']*100:+.2f}%")
        else:
            st.info("ETF / 槓桿 ETF 不直接套用一般個股法人籌碼權重，改以價格趨勢、波動與支撐壓力為主。")

        with st.expander("查看技術依據"):
            st.write(f"MA5：{lv['ma5']:.2f}")
            st.write(f"MA10：{lv['ma10']:.2f}")
            st.write(f"MA20：{lv['ma20']:.2f}")
            st.write(f"ATR14：{lv['atr']:.2f}")
            st.write(f"VWAP 近似值：{lv['vwap']:.2f}")
            st.caption("區間依近期高低、均線、ATR、昨高昨低與 VWAP 近似值建立，不使用單純固定百分比。")

        st.warning("本工具僅供交易規劃與資料分析；免費資料可能延遲，下單前請以券商即時行情確認。")
    except Exception as e:
        st.error(f"查詢失敗：{e}")
        st.caption("如果是 API 流量限制，可在上方 API 設定填入 FinMind Token。")
