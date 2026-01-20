import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. 設定頁面配置 ---
st.set_page_config(layout="wide", page_title="金開心-智能投資配置系統")

# --- 2. 資料讀取與清洗函數 ---
@st.cache_data # 快取資料，加速運作
def load_data():
    # 這裡假設您的檔案名稱為 'quote.csv'，請根據實際檔名修改
    # 注意：需處理 csv 編碼，通常 Excel 存出的 csv 是 big5 或 utf-8-sig
    try:
        df = pd.read_csv('金開心20251127(加入AI收益增長及雜幣券)NO PASS.xlsx - 報價.csv', encoding='utf-8-sig')
    except:
        # 如果讀取失敗，嘗試用 big5
        df = pd.read_csv('金開心20251127(加入AI收益增長及雜幣券)NO PASS.xlsx - 報價.csv', encoding='big5')
    
    # 清洗資料：將百分比字串轉為數字 (例如 "5.5%" -> 0.055)
    # 根據您的CSV，當期收益率可能是小數 (0.05) 或字串
    def clean_percentage(x):
        if isinstance(x, str):
            x = x.replace(',', '')
        try:
            return float(x)
        except:
            return 0.0

    # 確保關鍵欄位是數字
    df['當期收益率'] = df['當期收益率'].apply(clean_percentage)
    df['Offer Price'] = pd.to_numeric(df['Offer Price'], errors='coerce').fillna(100)
    
    # 建立一個顯示用的名稱 (結合代碼與名稱)
    # 處理欄位名稱可能有的空格
    col_map = {c: c.strip().replace('\n', '') for c in df.columns}
    df = df.rename(columns=col_map)
    
    # 假設第一欄是代碼，第二欄是名稱 (根據您的CSV結構)
    code_col = df.columns[0] 
    name_col = df.columns[1]
    df['Display_Name'] = df[code_col].astype(str) + " - " + df[name_col].astype(str)
    
    return df

# --- 主程式 ---
try:
    df = load_data()
except Exception as e:
    st.error(f"讀取資料失敗，請確認 CSV 檔案存在且格式正確。錯誤訊息: {e}")
    st.stop()

# --- 3. 側邊欄：配置設定 ---
st.sidebar.header("💼 投資組合配置")

# 選擇標的 (Multiselect)
selected_products = st.sidebar.multiselect(
    "請選擇投資標的 (可搜尋)",
    options=df['Display_Name'].unique(),
    default=df['Display_Name'].head(3) # 預設選前三檔
)

if not selected_products:
    st.warning("👈 請從左側側邊欄選擇至少一檔投資標的")
    st.stop()

# 過濾出選中的資料
portfolio = df[df['Display_Name'].isin(selected_products)].copy()

# --- 4. 動態輸入金額 ---
st.subheader("💰 資金分配試算")

# 使用 Streamlit 的 Data Editor 讓理專直接在表格上改金額
# 我們建立一個暫存的 dataframe 來讓使用者編輯
input_df = portfolio[['Display_Name', '幣別', '當期收益率', '配息頻率']].copy()
input_df['投資金額(原幣)'] = 100000.0 # 預設金額

# 顯示可編輯表格
edited_df = st.data_editor(
    input_df,
    column_config={
        "Display_Name": st.column_config.TextColumn("標的名稱", disabled=True),
        "幣別": st.column_config.TextColumn("幣別", disabled=True),
        "當期收益率": st.column_config.NumberColumn("當期收益率", format="%.2f%%", disabled=True),
        "配息頻率": st.column_config.TextColumn("頻率", disabled=True),
        "投資金額(原幣)": st.column_config.NumberColumn("投資金額", min_value=0, step=1000, format="$%d")
    },
    use_container_width=True,
    hide_index=True
)

# --- 5. 計算核心邏輯 ---
# 計算預估年配息金額 = 投資金額 * 當期收益率 (這裡做簡化計算，實際可加入匯率換算)
edited_df['預估年配息'] = edited_df['投資金額(原幣)'] * edited_df['當期收益率']
edited_df['預估月配息'] = edited_df['預估年配息'] / 12 # 簡化平均

total_investment = edited_df['投資金額(原幣)'].sum()
total_annual_income = edited_df['預估年配息'].sum()
avg_monthly_income = edited_df['預估月配息'].sum()

# 計算組合加權收益率
if total_investment > 0:
    portfolio_yield = (total_annual_income / total_investment) * 100
else:
    portfolio_yield = 0

# --- 6. 儀表板呈現 ---
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("總投資金額", f"${total_investment:,.0f}")
c2.metric("組合平均年化配息率", f"{portfolio_yield:.2f}%")
c3.metric("預估每月平均現金流", f"${avg_monthly_income:,.0f}")

st.divider()

# --- 7. 圖表視覺化 ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("##### 📊 資產配置佔比")
    fig_pie = px.pie(edited_df, values='投資金額(原幣)', names='Display_Name', hole=0.4)
    fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
    st.markdown("##### 💸 各標的貢獻現金流 (年)")
    fig_bar = px.bar(
        edited_df, 
        x='Display_Name', 
        y='預估年配息',
        text_auto='.2s',
        color='Display_Name'
    )
    fig_bar.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_bar, use_container_width=True)

# --- 8. 風險提示與詳細資料 ---
st.subheader("⚠️ 風險提示與詳細規格")

# 抓取並顯示重要的風險備註
risk_df = portfolio[['Display_Name', '產品風險屬性', '債券評等', '到期日', '備註']].copy()

# 若有 Call (贖回) 關鍵字，特別標示
def highlight_risk(val):
    if isinstance(val, str) and ("Call" in val or "贖回" in val):
        return "background-color: #ffe6e6; color: #cc0000; font-weight: bold;" # 紅底紅字
    return ""

st.dataframe(
    risk_df.style.map(highlight_risk, subset=['備註']),
    use_container_width=True,
    hide_index=True
)

# 匯出功能
csv = edited_df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    "📥 下載配置報告 (CSV)",
    csv,
    "investment_portfolio.csv",
    "text/csv",
    key='download-csv'
)
