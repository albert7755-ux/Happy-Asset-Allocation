import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="金開心現金流試算", layout="wide", page_icon="💰")

COLORS = ["#1565c0", "#c62828", "#2e7d32", "#6a1b9a", "#e65100", "#00838f"]
LABELS = ["A", "B", "C", "D", "E", "F"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');
* { font-family: 'Noto Sans TC', sans-serif; }
.bond-tag {
    display: inline-block;
    color: white;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 基金/ELN 對照表
# ==========================================
FUND_DB = {
    "AS07 PIMCO收益增長(美元後收)": {"name": "PIMCO收益增長(美元後收)", "annual_yield": 0.0900, "type": "FUND"},
    "駿利亨德森平衡T6(美元後收)(穩月配)": {"name": "駿利亨德森平衡基金T6(美元)(穩月配)", "annual_yield": 0.0850, "type": "FUND"},
    "AC18施羅德環球收息債券(美元)U-月配固定": {"name": "施羅德環球收息債券(美元)U-月配固定", "annual_yield": 0.0938, "type": "FUND"},
    "AP05富達全球優質債(美元後收)": {"name": "富達全球優質債券基金(B股C月配息美元)", "annual_yield": 0.0849, "type": "FUND"},
    "AP21富達存股優勢(美元後收)": {"name": "富達永續發展全球存股優勢基金(B股C月配息美元)", "annual_yield": 0.0819, "type": "FUND"},
    "FA23群益潛力多重(美元後收)": {"name": "群益潛力收益多重NB(月配型-美元)", "annual_yield": 0.0700, "type": "FUND"},
    "AG20安聯AI收益成長": {"name": "安聯AI收益成長基金-BMf9固定月配類股(美元)", "annual_yield": 0.0934, "type": "FUND"},
    "AS01 PIMCO多元收益(美元後收)": {"name": "PIMCO多元收益(美元後收)", "annual_yield": 0.0850, "type": "FUND"},
    "AU08貝萊德全球智慧數據股票入息(美元後收)": {"name": "貝萊德全球智慧數據股票入息基金B6美元", "annual_yield": 0.0743, "type": "FUND"},
    "AU07貝萊德環資配(美元後收)": {"name": "貝萊德環球資產配置基金B10美元", "annual_yield": 0.0660, "type": "FUND"},
    "AJ22鋒裕匯理基金歐元非投債-美元避險(後收)": {"name": "鋒裕匯理基金歐元非投資等級債券-美元避險", "annual_yield": 0.0791, "type": "FUND"},
    "AJ23鋒裕匯理基金歐元非投債-歐元(後收)": {"name": "鋒裕匯理基金歐元非投資等級債券-歐元", "annual_yield": 0.0586, "type": "FUND"},
    "AI10摩根歐洲策略-美元對沖(後收)": {"name": "摩根歐洲策略股息基金-美元對沖F股(每月派息)", "annual_yield": 0.0490, "type": "FUND"},
    "AI20摩根多重(美元對沖)(美元後收)": {"name": "摩根多重穩定月配息美元對沖F股", "annual_yield": 0.1100, "type": "FUND"},
    "AI25摩根環球非投資等級債券(美元對沖)(美元後收)": {"name": "摩根環球非投資等級債券(美元)-F股(穩定月配)", "annual_yield": 0.1100, "type": "FUND"},
    "AF12富蘭克林穩月(美元後收)": {"name": "富蘭克林穩定月收益基金美元F(Mdis)股", "annual_yield": 0.0821, "type": "FUND"},
    "AB15 聯博-新興市場多元(美元後收)": {"name": "聯博-新興市場多元收益基金ED月配級別美元", "annual_yield": 0.0551, "type": "FUND"},
    "AB35聯博美成(總報酬月配)(美元後收)": {"name": "聯博-美國成長基金EP(總報酬月配)級別美元", "annual_yield": 0.1259, "type": "FUND"},
    "AB37聯博優化波動(總報酬月配)(美元後收)": {"name": "聯博-優化波動股票基金EP(總報酬月配)級別美元", "annual_yield": 0.0885, "type": "FUND"},
    "AB13聯博全球多元收益(美元後收)": {"name": "聯博-全球多元收益ED月配級別", "annual_yield": 0.0824, "type": "FUND"},
    "AB03聯博美國收益(美元後收)": {"name": "聯博美國收益EA穩定月配", "annual_yield": 0.0781, "type": "FUND"},
    "59DF 聯博房貸收益(前收)": {"name": "聯博房貸收益AA穩月配", "annual_yield": 0.0888, "type": "FUND"},
    "AE02野村(愛爾蘭)美國非投資(美元後收)": {"name": "野村愛爾蘭美國非投資等級債券基金(BD美元類股)", "annual_yield": 0.1220, "type": "FUND"},
    "AG08安聯美元短期非投債(美元後收)": {"name": "安聯美元短年期非投資等級債券-BMg", "annual_yield": 0.0843, "type": "FUND"},
    "DT06富邦台美雙星(美元後收)": {"name": "富邦台美雙星多重NB月配", "annual_yield": 0.0904, "type": "FUND"},
    "ELN（月配12%）": {"name": "ELN", "annual_yield": 0.1200, "type": "ELN"},
}

# ==========================================
# 債券配息月份對照表
# ==========================================
BOND_PAY_MONTHS = {
    "US88579YBD22": (9, 3), "US084664CQ25": (8, 2), "XS1807174559": (4, 10),
    "US023135BJ40": (8, 2), "US375558BK80": (3, 9), "US037833CH12": (2, 8),
    "US002824BH26": (11, 5), "XS1508675508": (10, 4), "US02209SAV51": (9, 3),
    "US92343VCK89": (8, 2), "US594918BT09": (8, 2), "US125523CF53": (7, 1),
    "US20030NBU46": (7, 1), "US375558BD48": (3, 9), "US02079KBN63": (2, 8),
    "US30303M8X35": (11, 5), "US747525AK99": (5, 11), "US25468PDB94": (6, 12),
    "US717081DK61": (5, 11), "US449276AF17": (2, 8), "US02209SAR40": (1, 7),
    "US12572QAF28": (9, 3), "US037833AL42": (5, 11), "US084670BK32": (2, 8),
    "US594918BZ68": (2, 8), "US717081EC37": (12, 6), "US035242AM81": (2, 8),
    "US91159HJN17": (6, 12), "US55608KBG94": (11, 5), "US686330AR22": (9, 3),
    "USG91139AL26": (7, 1), "US92556HAC16": (5, 11), "US31428XCA28": (5, 11),
    "US09062XAG88": (5, 11), "US37045VAT70": (4, 10), "US854502AJ02": (11, 5),
    "US00206RCU41": (2, 8), "US94974BGU89": (12, 6), "US172967KR13": (5, 11),
    "US00206RCQ39": (5, 11), "US58013MFA71": (12, 6), "US42824CAY57": (10, 4),
    "US09062XAD57": (9, 3), "US37045VAJ98": (4, 10), "US61747YDY86": (1, 7),
    "US94974BGE48": (11, 5), "US172967HS33": (5, 11), "XS1049699926": (3, 9),
    "US404280AQ21": (3, 9), "US37045VAF76": (10, 4), "US92553PAP71": (3, 9),
    "US00206RBH49": (12, 6), "US71568QAB32": (10, 4), "US854502AA92": (9, 3),
    "US50076QAN60": (2, 8), "XS2885079702": (9, 3), "US46625HHF01": (5, 11),
    "US37045VAP58": (4, 10), "US126650CY46": (3, 9), "US38141GFD16": (10, 4),
    "US00206RDR03": (3, 9), "US404280AG49": (5, 11), "US38143YAC75": (5, 11),
    "US925524AX89": (4, 10), "US37045VAK61": (4, 10), "XS3151416727": (12, 6),
    "US06051GLU12": (9, 3), "XS2852920342": (7, 1), "US458140CA64": (8, 2),
    "US02079KBP12": (1, 7), "US30303MAE21": (11, 5), "US64110LBA35": (9, 3),
    "US03769MAC01": (8, 2), "US191216DS69": (10, 4), "US92343VGW81": (3, 9),
    "XS2747599509": (9, 3), "US29736RAU41": (9, 3), "US037833EW60": (2, 8),
    "US91324PEW86": (10, 4), "US532457CG18": (2, 8), "US91324PES74": (10, 4),
    "US459200KZ37": (2, 8), "US459200KV23": (9, 3), "US45866FAX24": (3, 9),
    "US872898AJ06": (4, 10), "US084664DB47": (3, 9), "US92343VGP31": (8, 2),
    "US828807DJ39": (7, 1), "US191216CQ13": (10, 4), "US254687FM36": (9, 3),
    "XS1982116136": (3, 9), "US58933YAW57": (9, 3), "US125523AK66": (3, 9),
}

# 債券當期收益率對照表
BOND_CURRENT_YIELD = {
    "US88579YBD22": 0.0489, "US084664CQ25": 0.0484, "XS1807174559": 0.0520,
    "US023135BJ40": 0.0476, "US375558BK80": 0.0483, "US037833CH12": 0.0472,
    "US002824BH26": 0.0505, "XS1508675508": 0.0518, "US02209SAV51": 0.0498,
    "US92343VCK89": 0.0520, "US594918BT09": 0.0442, "US125523CF53": 0.0522,
    "US20030NBU46": 0.0469, "US375558BD48": 0.0508, "US02079KBN63": 0.0521,
    "US30303M8X35": 0.0546, "US747525AK99": 0.0513, "US25468PDB94": 0.0468,
    "US717081DK61": 0.0481, "US449276AF17": 0.0543, "US02209SAR40": 0.0550,
    "US12572QAF28": 0.0513, "US037833AL42": 0.0442, "US084670BK32": 0.0460,
    "US594918BZ68": 0.0412, "US717081EC37": 0.0415, "US035242AM81": 0.0465,
    "US91159HJN17": 0.0543, "US55608KBG94": 0.0521, "US686330AR22": 0.0498,
    "USG91139AL26": 0.0442, "US92556HAC16": 0.0741, "US31428XCA28": 0.0544,
    "US09062XAG88": 0.0468, "US37045VAT70": 0.0595, "US854502AJ02": 0.0541,
    "US00206RCU41": 0.0556, "US94974BGU89": 0.0534, "US172967KR13": 0.0531,
    "US00206RCQ39": 0.0530, "US58013MFA71": 0.0517, "US42824CAY57": 0.0604,
    "US09062XAD57": 0.0543, "US37045VAJ98": 0.0564, "US61747YDY86": 0.0492,
    "US94974BGE48": 0.0525, "US172967HS33": 0.0546, "XS1049699926": 0.0559,
    "US404280AQ21": 0.0530, "US37045VAF76": 0.0600, "US92553PAP71": 0.0638,
    "US00206RBH49": 0.0492, "US71568QAB32": 0.0560, "US854502AA92": 0.0527,
    "US50076QAN60": 0.0594, "XS2885079702": 0.0515, "US46625HHF01": 0.0557,
    "US37045VAP58": 0.0524, "US126650CY46": 0.0495, "US38141GFD16": 0.0594,
    "US00206RDR03": 0.0504, "US404280AG49": 0.0576, "US38143YAC75": 0.0582,
    "US925524AX89": 0.0700, "US37045VAK61": 0.0598, "XS3151416727": 0.0533,
    "US06051GLU12": 0.0545, "XS2852920342": 0.0556, "US458140CA64": 0.0423,
    "US02079KBP12": 0.0565, "US30303MAE21": 0.0563, "US64110LBA35": 0.0540,
    "US03769MAC01": 0.0580, "US191216DS69": 0.0530, "US92343VGW81": 0.0550,
    "XS2747599509": 0.0575, "US29736RAU41": 0.0515, "US037833EW60": 0.0485,
    "US91324PEW86": 0.0505, "US532457CG18": 0.0488, "US91324PES74": 0.0588,
    "US459200KZ37": 0.0510, "US459200KV23": 0.0490, "US45866FAX24": 0.0495,
    "US872898AJ06": 0.0450, "US084664DB47": 0.0385, "US92343VGP31": 0.0388,
    "US828807DJ39": 0.0380, "US191216CQ13": 0.0420, "US254687FM36": 0.0275,
    "XS1982116136": 0.0438, "US58933YAW57": 0.0400,
    "US125523AK66": 0.0490,
}

# 債券LOCAL_DB（簡化版，只含issuer/coupon）
LOCAL_DB = {
    "US88579YBD22": {"issuer": "3M 公司債1", "coupon": 4.0},
    "US084664CQ25": {"issuer": "波克夏海瑟威金融公司債1", "coupon": 4.2},
    "XS1807174559": {"issuer": "卡達政府國際債1", "coupon": 5.103},
    "US023135BJ40": {"issuer": "亞馬遜公司債1", "coupon": 4.05},
    "US375558BK80": {"issuer": "吉利德科學公司債1", "coupon": 4.15},
    "US037833CH12": {"issuer": "蘋果公司債11", "coupon": 3.95},
    "US002824BH26": {"issuer": "ABB金融公司債1", "coupon": 4.375},
    "XS1508675508": {"issuer": "阿布達比主權債1", "coupon": 3.125},
    "US02209SAV51": {"issuer": "高特利集團公司債2", "coupon": 5.375},
    "US92343VCK89": {"issuer": "威瑞森電信公司債8", "coupon": 4.125},
    "US594918BT09": {"issuer": "微軟公司債5", "coupon": 3.45},
    "US125523CF53": {"issuer": "信諾公司債2", "coupon": 5.375},
    "US20030NBU46": {"issuer": "康卡斯特公司債1", "coupon": 4.049},
    "US375558BD48": {"issuer": "吉利德科學公司債2", "coupon": 4.75},
    "US02079KBN63": {"issuer": "Alphabet公司債4", "coupon": 3.375},
    "US30303M8X35": {"issuer": "Meta平台公司債4", "coupon": 5.75},
    "US747525AK99": {"issuer": "高通公司債1", "coupon": 4.65},
    "US25468PDB94": {"issuer": "迪士尼公司債3", "coupon": 3.8},
    "US717081DK61": {"issuer": "輝瑞公司債3", "coupon": 4.45},
    "US449276AF17": {"issuer": "IBM公司債2", "coupon": 4.25},
    "US02209SAR40": {"issuer": "高特利集團公司債1", "coupon": 5.375},
    "US12572QAF28": {"issuer": "CVS健康公司債1", "coupon": 5.05},
    "US037833AL42": {"issuer": "蘋果公司債3", "coupon": 3.0},
    "US084670BK32": {"issuer": "波克夏海瑟威公司債1", "coupon": 4.2},
    "US594918BZ68": {"issuer": "微軟公司債7", "coupon": 3.3},
    "US717081EC37": {"issuer": "輝瑞公司債5", "coupon": 4.0},
    "US035242AM81": {"issuer": "百威英博公司債1", "coupon": 4.375},
    "US91159HJN17": {"issuer": "美國合眾銀行公司債1", "coupon": 5.85},
    "US55608KBG94": {"issuer": "麥當勞公司債1", "coupon": 5.15},
    "US686330AR22": {"issuer": "奧克蘇斯公司債1", "coupon": 5.0},
    "USG91139AL26": {"issuer": "怡和控股公司債1", "coupon": 3.5},
    "US92556HAC16": {"issuer": "維康公司債1", "coupon": 6.875},
    "US31428XCA28": {"issuer": "聯邦快遞公司債1", "coupon": 5.25},
    "US09062XAG88": {"issuer": "生物基因公司債1", "coupon": 3.15},
    "US37045VAT70": {"issuer": "通用汽車公司債2", "coupon": 5.75},
    "US854502AJ02": {"issuer": "史丹利百得公司債1", "coupon": 4.85},
    "US00206RCU41": {"issuer": "AT&T公司債2", "coupon": 3.8},
    "US94974BGU89": {"issuer": "威爾斯法哥公司債1", "coupon": 5.574},
    "US172967KR13": {"issuer": "花旗集團公司債1", "coupon": 5.61},
    "US00206RCQ39": {"issuer": "AT&T公司債1", "coupon": 5.15},
    "US58013MFA71": {"issuer": "麥克森公司債1", "coupon": 5.45},
    "US42824CAY57": {"issuer": "赫斯公司債1", "coupon": 6.0},
    "US09062XAD57": {"issuer": "生物基因公司債2", "coupon": 5.2},
    "US37045VAJ98": {"issuer": "通用汽車公司債1", "coupon": 5.4},
    "US61747YDY86": {"issuer": "摩根士丹利公司債1", "coupon": 5.0},
    "US94974BGE48": {"issuer": "威爾斯法哥公司債2", "coupon": 5.013},
    "US172967HS33": {"issuer": "花旗集團公司債2", "coupon": 5.3},
    "XS1049699926": {"issuer": "渣打銀行公司債1", "coupon": 4.3},
    "US71568QAB32": {"issuer": "聯合健康集團債7", "coupon": 5.875},
    "US02079KBP12": {"issuer": "Alphabet公司債6", "coupon": 5.65},
    "US30303MAE21": {"issuer": "Meta平台公司債9", "coupon": 5.625},
    "US64110LBA35": {"issuer": "網飛公司債3", "coupon": 5.4},
    "US03769MAC01": {"issuer": "阿波羅全球公司債1", "coupon": 5.8},
    "US191216DS69": {"issuer": "可口可樂公司債5", "coupon": 5.3},
    "US92343VGW81": {"issuer": "威瑞森電信公司債12", "coupon": 5.5},
    "XS2747599509": {"issuer": "沙烏地阿拉伯債7", "coupon": 5.75},
    "US29736RAU41": {"issuer": "雅詩蘭黛公司債3", "coupon": 5.15},
    "US037833EW60": {"issuer": "蘋果公司債14", "coupon": 4.85},
    "US125523AK66": {"issuer": "信諾公司債1", "coupon": 4.9},
}

def get_bond_pay_months(isin):
    return BOND_PAY_MONTHS.get(isin, (1, 7))

# ==========================================
# 主介面
# ==========================================
st.markdown("## 💰 金開心現金流試算工具")
st.markdown("混搭債券、基金、ELN，試算每月現金流與年化配息率")
st.markdown("---")

# 投資本金
principal = st.number_input(
    "投資總本金（元）",
    min_value=100000,
    max_value=1000000000,
    value=10000000,
    step=1000000,
    format="%d"
)

# 選擇幾個標的
n_cf = st.radio("投資幾個標的？", [2, 3, 4, 5, 6], horizontal=True, key="cf_n")
st.markdown("---")

# 建立所有可選標的
bond_options = {
    f"{v['issuer']}（{k}）": {
        "isin": k, "type": "BOND", "name": v["issuer"],
        "annual_yield": BOND_CURRENT_YIELD.get(k, v["coupon"] / 100)
    }
    for k, v in LOCAL_DB.items()
}
fund_options = {
    f"【基金/ELN】{v['name']}": {
        "isin": k, "type": v["type"], "name": v["name"], "annual_yield": v["annual_yield"]
    }
    for k, v in FUND_DB.items()
}
all_cf_options = dict(sorted({**bond_options, **fund_options}.items()))
all_cf_keys = ["（請選擇）"] + list(all_cf_options.keys())

# 配置各標的
cf_items = []
cols_cf = st.columns(n_cf)

for i in range(n_cf):
    with cols_cf[i]:
        color = COLORS[i % len(COLORS)]
        label = LABELS[i]
        st.markdown(f'<span class="bond-tag" style="background:{color}">標的 {label}</span>', unsafe_allow_html=True)

        selected_cf = st.selectbox(
            "選擇標的",
            options=all_cf_keys,
            key=f"cf_sel_{i}"
        )

        if selected_cf != "（請選擇）":
            item = all_cf_options[selected_cf]

            # 換了標的就自動更新收益率
            if st.session_state.get(f"cf_last_sel_{i}") != selected_cf:
                st.session_state[f"cf_yield_{i}"] = round(item["annual_yield"] * 100, 2)
                st.session_state[f"cf_last_sel_{i}"] = selected_cf

            default_pct = round(100.0 / n_cf, 1)
            pct = st.number_input(
                "投資比例 %",
                min_value=0.0, max_value=100.0,
                value=default_pct, step=1.0,
                key=f"cf_pct_{i}", format="%.1f"
            )
            yield_pct = st.number_input(
                "當期年化收益率 %（可修改）",
                min_value=0.0, max_value=30.0,
                step=0.01,
                key=f"cf_yield_{i}", format="%.2f"
            )
            amt = principal * pct / 100
            annual_income = amt * yield_pct / 100
            monthly_income = annual_income / 12

            st.markdown(f"**投資金額：** ${amt:,.0f}")
            st.markdown(f"**預估年息：** ${annual_income:,.0f}")
            st.markdown(f"**預估月息：** ${monthly_income:,.0f}")

            cf_items.append({
                "label": label,
                "color": color,
                "name": item["name"],
                "type": item["type"],
                "isin": item["isin"],
                "pct": pct,
                "amount": amt,
                "yield_pct": yield_pct,
                "annual_income": annual_income,
                "monthly_income": monthly_income,
            })

# ==========================================
# 計算總覽
# ==========================================
if cf_items:
    st.markdown("---")
    total_pct = sum(x["pct"] for x in cf_items)
    total_income = sum(x["annual_income"] for x in cf_items)
    avg_yield = total_income / principal * 100 if principal > 0 else 0

    months = ["一月", "二月", "三月", "四月", "五月", "六月",
              "七月", "八月", "九月", "十月", "十一月", "十二月"]
    monthly_total = [0.0] * 12
    month_details = {m: [] for m in range(1, 13)}

    for item in cf_items:
        if item["type"] in ("FUND", "ELN"):
            monthly_amt = item["annual_income"] / 12
            for m in range(1, 13):
                monthly_total[m - 1] += monthly_amt
                month_details[m].append((item["label"], item["name"][:12], monthly_amt))
        else:
            m1, m2 = get_bond_pay_months(item["isin"])
            semi_amt = item["annual_income"] / 2
            for m in [m1, m2]:
                monthly_total[m - 1] += semi_amt
                month_details[m].append((item["label"], item["name"][:12], semi_amt))

    max_m_idx = monthly_total.index(max(monthly_total))

    # KPI 卡片
    st.markdown(f"""
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px;">
        <div style="flex:1;min-width:150px;background:#f0f4ff;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:0.8rem;color:#666;">💰 投資本金</div>
            <div style="font-size:1.3rem;font-weight:700;color:#1a2744;">${principal:,.0f}</div>
        </div>
        <div style="flex:1;min-width:150px;background:#f0f4ff;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:0.8rem;color:#666;">📊 資金配置</div>
            <div style="font-size:1.3rem;font-weight:700;color:{'#2e7d32' if abs(total_pct - 100) < 0.1 else '#c62828'};">{total_pct:.1f}%</div>
            <div style="font-size:0.75rem;color:#888;">{'✅ 已滿' if abs(total_pct - 100) < 0.1 else f'⚠️ 還差{100 - total_pct:.1f}%'}</div>
        </div>
        <div style="flex:1;min-width:150px;background:#fff9e6;border:2px solid #c8a84b;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:0.8rem;color:#666;">📈 年化配息率</div>
            <div style="font-size:1.6rem;font-weight:700;color:#b8860b;">{avg_yield:.2f}%</div>
        </div>
        <div style="flex:1;min-width:150px;background:#f0f4ff;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:0.8rem;color:#666;">🎯 預估年領總息</div>
            <div style="font-size:1.3rem;font-weight:700;color:#1a2744;">${total_income:,.0f}</div>
        </div>
        <div style="flex:1;min-width:150px;background:#f0f4ff;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:0.8rem;color:#666;">📅 預估月均領息</div>
            <div style="font-size:1.3rem;font-weight:700;color:#1a2744;">${total_income / 12:,.0f}</div>
        </div>
        <div style="flex:1;min-width:150px;background:#f0f4ff;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:0.8rem;color:#666;">🗓️ 最高領息月份</div>
            <div style="font-size:1.1rem;font-weight:700;color:#1565c0;">{months[max_m_idx]}</div>
            <div style="font-size:0.85rem;color:#1565c0;">${monthly_total[max_m_idx]:,.0f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 逐月現金流明細
    st.markdown("---")
    st.subheader("📅 逐月現金流明細")

    cf_html = '<table style="width:100%;border-collapse:collapse;font-size:0.85rem;border-radius:8px;overflow:hidden;">'
    cf_html += '<thead><tr>'
    cf_html += '<th style="background:#1a2744;color:white;padding:8px 12px;text-align:left;">月份</th>'
    for item in cf_items:
        cf_html += f'<th style="background:{item["color"]};color:white;padding:8px 12px;text-align:center;">{item["label"]}. {item["name"][:8]}</th>'
    cf_html += '<th style="background:#c8a84b;color:white;padding:8px 12px;text-align:center;">當月合計</th>'
    cf_html += '</tr></thead><tbody>'

    for m_idx, month_name in enumerate(months):
        m = m_idx + 1
        bg = "#f0f4ff" if m_idx % 2 == 0 else "white"
        cf_html += f'<tr style="background:{bg};">'
        cf_html += f'<td style="padding:7px 12px;font-weight:700;color:#1a2744;">{month_name}</td>'
        for item in cf_items:
            if item["type"] in ("FUND", "ELN"):
                val = item["annual_income"] / 12
                cf_html += f'<td style="padding:7px 12px;text-align:right;">${val:,.0f}</td>'
            else:
                m1, m2 = get_bond_pay_months(item["isin"])
                if m in [m1, m2]:
                    val = item["annual_income"] / 2
                    cf_html += f'<td style="padding:7px 12px;text-align:right;font-weight:600;color:#1565c0;">${val:,.0f}</td>'
                else:
                    cf_html += '<td style="padding:7px 12px;text-align:center;color:#ccc;">—</td>'
        total_m = monthly_total[m_idx]
        cf_html += f'<td style="padding:7px 12px;text-align:right;font-weight:700;color:#c8a84b;">${total_m:,.0f}</td>'
        cf_html += '</tr>'

    cf_html += '<tr style="background:#1a2744;">'
    cf_html += '<td style="padding:8px 12px;color:#ffd700;font-weight:700;">全年合計</td>'
    for item in cf_items:
        cf_html += f'<td style="padding:8px 12px;text-align:right;color:white;font-weight:700;">${item["annual_income"]:,.0f}</td>'
    cf_html += f'<td style="padding:8px 12px;text-align:right;color:#ffd700;font-weight:700;">${total_income:,.0f}</td>'
    cf_html += '</tr></tbody></table>'
    st.markdown(cf_html, unsafe_allow_html=True)

    # 月現金流圖表
    st.markdown("---")
    st.subheader("📊 月現金流圖表")
    fig_cf = go.Figure()
    fig_cf.add_trace(go.Bar(
        x=months,
        y=monthly_total,
        marker_color=[COLORS[i % len(COLORS)] for i in range(12)],
        text=[f"${v:,.0f}" for v in monthly_total],
        textposition="outside",
        name="當月合計"
    ))
    fig_cf.update_layout(
        yaxis_title="配息金額（元）",
        height=380,
        plot_bgcolor="#f8f9ff",
        paper_bgcolor="white",
        showlegend=False,
        margin=dict(t=20, b=40)
    )
    st.plotly_chart(fig_cf, use_container_width=True)

    # 投資組合配置
    st.subheader("🥧 投資組合配置")
    pie_col1, pie_col2 = st.columns(2)
    with pie_col1:
        fig_pie = go.Figure(go.Pie(
            labels=[f"{x['label']}. {x['name'][:10]}" for x in cf_items],
            values=[x["amount"] for x in cf_items],
            marker_colors=[x["color"] for x in cf_items],
            hole=0.4
        ))
        fig_pie.update_layout(title="資金分配比例", height=300, margin=dict(t=40, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)
    with pie_col2:
        fig_pie2 = go.Figure(go.Pie(
            labels=[f"{x['label']}. {x['name'][:10]}" for x in cf_items],
            values=[x["annual_income"] for x in cf_items],
            marker_colors=[x["color"] for x in cf_items],
            hole=0.4
        ))
        fig_pie2.update_layout(title="年息貢獻比例", height=300, margin=dict(t=40, b=0))
        st.plotly_chart(fig_pie2, use_container_width=True)

    st.warning("⚠️ 以上試算均為估計值，配息金額以各機構實際公告為準。僅供內部教育訓練使用，請勿外流。")

st.markdown("---")
st.caption("本工具僅供內部教育訓練使用，請勿外流。")
