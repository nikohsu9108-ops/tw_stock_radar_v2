# 台股籌碼實戰雷達 V2

部署檔案：
- app.py
- requirements.txt
- .streamlit/config.toml

功能：
- 股票代號或中文名稱搜尋
- 上市 / 上櫃 / ETF / 槓桿 ETF
- 當沖 / 隔日 / 波段
- 籌碼與融資融券
- 台股合法跳動單位
- 進場 / 停損 / 停利 / 突破 / 不追價
- 價格邏輯硬性檢查：停損 < 進場 < 停利1 < 停利2

資料來源：FinMind API v4
API 文件：https://api.finmindtrade.com/docs

部署到 Streamlit Community Cloud：
1. 建立 GitHub 帳號
2. 建立 repository
3. 上傳以上檔案
4. 到 Streamlit Community Cloud 建立 App
5. Main file path 選 app.py
