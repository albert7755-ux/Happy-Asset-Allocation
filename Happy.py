import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. 設定頁面配置 ---
st.set_page_config(layout="wide", page_title="金開心-智能投資配置系統")

st.title("🏦 金開心 - 智能投資組合配置器")

# --- 2. 側邊欄：檔案上傳 ---
st.sidebar.header("📁 資料匯入")
uploaded_file = st.sidebar.file_uploader("請上傳報價單 (CSV 格式)", type=['csv'])

# --- 3. 資料讀取與清洗函數 ---
@st.cache_data
def load_data(file):
    try:
        # 嘗試用 utf-8-sig 讀取 (Excel 常見格式)
        df = pd.read_csv(file, encoding='utf-8-sig')
    except:
        # 如果失敗，嘗試用 big5 (中文舊格式)
        file.seek(0) # 重置讀取指標
        df = pd.read_csv(file, encoding='big5')
    
    # 清洗資料：處理百分比與價格
    def clean_percentage(x):
        if isinstance(x, str):
            x = x.replace(',', '').replace('%', '') # 移除逗號和%
            try:
                return float(x) / 100 if float(x) > 1 else float(x) # 簡單判斷是 5% 還是 0.05
            except:
                return 0.0
        return float(x) if x else 0.0

    # 確保關鍵欄位存在與格式正確
    # 自動尋找類似名稱的欄位，增加容錯率
    cols = df.columns.tolist()
    
    # 對應您的 CSV 欄位名稱 (根據您提供的檔案內容微調)
    # 假設您的 CSV 欄位可能有 "當期收益率", "Offer Price", "債券名稱" 等
    yield_col = next((c for c in cols if "當期收益" in c), None)
    price_col = next((c for c in cols if "Offer" in c or "Price" in c), None)
    name_col = next((c for c in cols if "名稱" in c), cols[1] if len(cols)>1 else cols[0])
    code_col = cols[0] # 假設第一欄是代碼

    if yield_col:
        df['當期收益率_Clean'] = df[yield_col].apply(clean_percentage)
    else:
        df['當期收益率_Clean'] = 0.0

    if price_col:
        df['Offer Price_Clean'] = pd.to_numeric(df[price_col], errors='coerce').fillna(100)
    
    # 建立顯示名稱
    df['Display_Name'] = df[code_col].astype(str) + " - " + df[name_col].astype(str)
    
    # 處理風險備註
    note_col = next((c for c in cols if "備註" in c), None)
    df['備註_Clean'] = df[note_col].fillna('') if note_col else ''
    
    return df

# --- 主程式邏輯 ---
if uploaded_file is None:
    st.info("👈 請從左側側邊欄上傳您的 `報價.csv` 檔案以開始使用")
    st.markdown("""
    ### 使用說明：
    1. 點擊左側 **「Browse files」** 按鈕。
    2. 選擇您電腦中的報價 CSV 檔。
    3. 系統將自動讀取並產生配置介面。
    """)
    st.stop() # 停止執行後續程式碼，直到有檔案為止

try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(f"檔案讀取錯誤，請確認 CSV 格式。錯誤訊息: {e}")
    st.stop()

# --- 4. 側邊欄：配置設定 ---
st.sidebar.divider()
st.sidebar.header("💼 投資組合選股")

# 選擇標的
selected_products = st.sidebar.multiselect(
    "選擇投資標的 (可多選/搜尋)",
    options=df['Display_Name'].unique(),
    default=df['Display_Name'].head(3).tolist()
)

if not selected_products:
    st.warning("請選擇至少一檔投資標的")
    st.stop()

# 過濾出選中的資料
portfolio = df[df['Display_Name'].isin(selected_products)].copy()

# --- 5. 動態輸入金額 ---
st.subheader("💰 資金分配與試算")
st.caption("請直接在下方表格修改「投資金額」，試算結果會即時更新")

# 準備編輯用的 DataFrame
input_df = portfolio[['Display_Name', '當期收益率_Clean', '備註_Clean']].copy()
input_df['投資金額(原幣)'] = 100000.0 # 預設金額

# 顯示可編輯表格
edited_df = st.data_editor(
    input_df,
    column_config={
        "Display_Name": st.column_config.TextColumn("標的名稱", disabled=True),
        "當期收益率_Clean": st.column_config.NumberColumn("當期收益率", format="%.2f%%", disabled=True),
        "備註_Clean": st.column_config.TextColumn("備註", disabled=True),
        "投資金額(原幣)": st.column_config.NumberColumn("投資金額", min_value=0, step=10000, format="$%d")
    },
    use_container_width=True,
    hide_index=True,
    num_rows="fixed"
)

# --- 6. 計算核心邏輯 ---
edited_df['預估年配息'] = edited_df['投資金額(原幣)'] * edited_df['當期收益率_Clean']
edited_df['預估月配息'] = edited_df['預估年配息'] / 12

total_investment = edited_df['投資金額(原幣)'].sum()
total_annual_income = edited_df['預估年配息'].sum()
avg_monthly_income = edited_df['預估月配息'].sum()

# 避免除以零
if total_investment > 0:
    portfolio_yield = (total_annual_income / total_investment)
else:
    portfolio_yield = 0

# --- 7. 儀表板呈現 ---
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("總投資金額", f"${total_investment:,.0f}")
c2.metric("組合平均年化配息率", f"{portfolio_yield:.2%}")
c3.metric("預估每月平均現金流", f"${avg_monthly_income:,.0f}")

st.divider()

# --- 8. 圖表視覺化 ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("##### 📊 資產配置佔比")
    if total_investment > 0:
        fig_pie = px.pie(edited_df, values='投資金額(原幣)', names='Display_Name', hole=0.4)
        fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("請輸入投資金額以顯示圖表")

with col_chart2:
    st.markdown("##### 💸 各標的貢獻現金流 (年)")
    if total_investment > 0:
        fig_bar = px.bar(
            edited_df, 
            x='Display_Name', 
            y='預估年配息',
            text_auto='.2s',
            color='Display_Name'
        )
        fig_bar.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_bar, use_container_width=True)

# --- 9. 風險提示 ---
st.subheader("⚠️ 風險提示與備註")

def highlight_risk(val):
    if isinstance(val, str) and ("Call" in val or "贖回" in val):
        return "background-color: #ffcccc; color: #cc0000; font-weight: bold;"
    return ""

st.dataframe(
    edited_df[['Display_Name', '備註_Clean']].style.map(highlight_risk, subset=['備註_Clean']),
    use_container_width=True,
    hide_index=True
)
