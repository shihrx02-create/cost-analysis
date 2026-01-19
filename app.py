import streamlit as st
import pandas as pd
import base64
import requests
import json
from io import BytesIO

# reportlab 已移除

# --- 1. 配置與中英對照表 ---
PROCESS_TRANSLATIONS = {
    "校車": "Calibration",
    "車床": "Lathe",
    "手工清洗": "Remove oil by hydrocarbon",
    "清洗": "Remove oil by hydrocarbon",
    "去油": "Remove oil by hydrocarbon",
    "自動清洗": "Remove oil by hydrocarbon",
    "修內徑加工": "Inner Diameter Processing",
    "包裝": "Packing",
    "熱處理": "Heat Treatment",
    "風切防鏽": "Anti-Rust",
    "清點數量": "Counting",
    "高週波": "High Frequency",
    "染黑": "Black Oxide",
    "巡牙": "Thread Inspection",
    "研磨": "Grinding",
    "拋光": "Polishing",
    "陽極": "Anodizing",
    "電鍍": "Plating",
    "噴砂": "Sandblasting",
    "刻字": "Laser Marking",
    "CNC加工": "CNC Machining",
    "CNC車床": "CNC Lathe",
    "CNC銑床": "CNC Milling",
    "CNC放電": "CNC EDM",
    "CNC線切割": "CNC Wire Cutting",
    "CNC磨床": "CNC Grinding",
    "CNC火花機": "CNC Spark Machine",
    }

# 翻譯快取（避免重複翻譯）
translation_cache = {}

# 成本項目的中英翻譯
COST_ITEM_TRANSLATIONS = {
    "總投入數量": "Total Input Quantity",
    "良品數量": "Good Product Quantity",
    "廢品數量": "Defective Quantity",
    "投入成本": "Input Cost",
    "加工成本": "Processing Cost",
    "外包成本": "Outsourcing Cost",
    "總成本": "Total Cost",
    "單顆成本": "Unit Cost",
    "目前售價": "Current Selling Price",
    "建議售價 (毛利潤20%)": "Suggested Selling Price (20% Profit Margin)",
    "建議售價(毛利潤20%)": "Suggested Selling Price (20% Profit Margin)"
}

def clean_process_name(name):
    if not isinstance(name, str): return "-"
    # 移除排除詞
    for word in ["廠內", "廠外", "託外", "外包", "委外"]:
        name = name.replace(word, "")
    # 移除數字後綴(如 風切防鏽3 -> 風切防鏽)
    import re
    clean_name = re.sub(r'\d+$', '', name).strip()
    # 移除所有空格
    clean_name = clean_name.replace(" ", "").replace("　", "")
    
    # 特殊匹配：包含「校車」的都識別為 Calibration
    if "校車" in clean_name:
        eng_name = "Calibration"
        clean_name = clean_name  # 保留原始名稱如「校車A」
    # 先查預設字典
    elif clean_name in PROCESS_TRANSLATIONS:
        eng_name = PROCESS_TRANSLATIONS[clean_name]
    else:
        # 如果不在字典裡，自動翻譯
        eng_name = auto_translate(clean_name)
    
    # 如果是清洗類工序，統一改成「碳氫去油處理」
    if eng_name == "Remove oil by hydrocarbon" or clean_name in ["手工清洗", "清洗", "去油", "自動清洗"]:
        clean_name = "碳氫去油處理"
        eng_name = "Remove oil by hydrocarbon"
    
    return f"{clean_name} | {eng_name}"

def auto_translate(text):
    """自動翻譯中文為英文（使用免費 API）"""
    if not text or not isinstance(text, str):
        return text
    
    # 檢查快取
    if text in translation_cache:
        return translation_cache[text]
    
    try:
        # 使用 MyMemory 免費翻譯 API（無需認證）
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": text,
            "langpair": "zh-CN|en"
        }
        response = requests.get(url, params=params, timeout=5)
        result = response.json()
        
        if result.get("responseStatus") == 200:
            translated = result.get("responseData", {}).get("translatedText", text)
            # 避免重複翻譯標記
            if translated != "[object Object]" and translated != text:
                translation_cache[text] = translated
                return translated
    except Exception as e:
        pass
    
    # 如果翻譯失敗，回傳原文
    translation_cache[text] = text
    return text

def get_cost_item_label(item_name):
    """取得成本項目的中英標籤"""
    if not isinstance(item_name, str):
        return "-"
    eng_name = COST_ITEM_TRANSLATIONS.get(item_name, item_name)
    return f"{item_name} | {eng_name}"

# --- 2. 數值擷取邏輯 ---
def get_val(df, row_label, col_idx, rate=1.0):
    """
    從 DataFrame 中提取特定值
    基於 CSV 結構：
    - 現況（左側）: 第 0-12 欄
    - 評估（右側）: 第 13-25 欄
    """
    try:
        # 在整個 DataFrame 中搜尋該標籤
        for row_num in range(len(df)):
            found_positions = []
            
            # 先找出所有符合該標籤的位置
            for col_num in range(min(26, len(df.columns))):
                cell_val = str(df.iloc[row_num, col_num]) if pd.notna(df.iloc[row_num, col_num]) else ""
                if row_label in cell_val:
                    found_positions.append(col_num)
            
            # 根據 col_idx 選擇適合的位置
            if col_idx == "current":
                # 現況在左側 (0-12 欄) - 優先選擇左邊的標籤
                search_positions = [p for p in found_positions if p <= 12]
                if not search_positions and found_positions:
                    search_positions = [found_positions[0]]
            else:
                # 評估在右側 (13-25 欄) - 優先選擇右邊的標籤
                search_positions = [p for p in found_positions if p >= 13]
                if not search_positions and found_positions:
                    search_positions = [found_positions[-1]]
            
            # 從選中的位置開始往右搜尋數值
            for col_num in search_positions:
                for offset in range(1, 5):
                    if col_num + offset < len(df.columns):
                        val_str = str(df.iloc[row_num, col_num + offset]) if pd.notna(df.iloc[row_num, col_num + offset]) else ""
                        if is_number(val_str):
                            num = float(val_str.replace(',', '').replace('，', ''))
                            return num / rate  # 返回未格式化的數值
        
        return "-"
    except Exception as e:
        return "-"

def is_number(val):
    """判斷字串是否為數字"""
    try:
        if isinstance(val, str):
            val = val.strip().replace(',', '').replace('，', '')
            if not val or val == '-' or val == '—':
                return False
            float(val)
            return True
        elif isinstance(val, (int, float)):
            return not pd.isna(val)
        return False
    except:
        return False

def format_quantity(value):
    """格式化數量為整數（無小數點）"""
    if value == "-" or isinstance(value, str):
        return value
    try:
        return str(int(round(float(value))))
    except:
        return "-"

def format_price(value):
    """格式化金額為2位小數"""
    if value == "-" or isinstance(value, str):
        return value
    try:
        return f"{float(value):.2f}"
    except:
        return "-"


# PDF 函數已移除

# --- 3. HTML 模板生成 ---
def generate_html(data):
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            body { 
                font-family: Arial, Helvetica, sans-serif; 
                margin: 20px; 
                line-height: 1.6;
                color: #333;
            }
            h1 { 
                text-align: center;
                color: #000;
                border-bottom: 2px solid #333;
                padding-bottom: 10px;
            }
            .container { 
                display: flex; 
                gap: 30px; 
                margin: 20px 0;
            }
            .section { 
                flex: 1;
                padding: 15px;
                border: 1px solid #ddd;
                background: #fafafa;
            }
            .section h2 {
                font-size: 1.1em;
                color: #333;
                margin: 0 0 15px 0;
            }
            table { 
                width: 100%; 
                border-collapse: collapse;
                background: white;
            }
            th, td { 
                border: 1px solid #ccc; 
                padding: 8px;
                text-align: center;
            }
            th { 
                background-color: #e0e0e0;
                font-weight: bold;
            }
            .highlight { 
                background-color: #e3f2fd;
                font-weight: bold;
            }
            .process-section {
                margin-top: 30px;
                padding: 15px;
                border: 1px solid #ddd;
                background: #fafafa;
            }
            .process-section h2 {
                font-size: 1.1em;
                color: #333;
                margin: 0 0 15px 0;
            }
            .footer {
                text-align: center;
                color: #999;
                font-size: 0.9em;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
            }
        </style>
    </head>
    <body>
        <h1>成本分析 | Cost Analysis | """ + str(data['part_no']) + """</h1>
        <div class="container">
            <div class="section">
                <h2>現況：成本分析 | Current Situation: Cost Analysis</h2>
                <table>
                    <tr><th>項目 | Item</th><th>數量 | Quantity</th><th>百分比 | Percentage</th><th>成本 (""" + str(data['currency']) + """) | Cost (""" + str(data['currency']) + """)</th></tr>
                    <tr><td>總投入數量 | Total Input Quantity</td><td>""" + str(data['c_total_qty']) + """</td><td>-</td><td>""" + str(data['c_total_input_cost']) + """</td></tr>
                    <tr><td>良品數量 | Good Product Quantity</td><td>""" + str(data['c_good_qty']) + """</td><td>""" + str(data['c_good_rate']) + """%</td><td>-</td></tr>
                    <tr><td>廢品數量 | Defective Quantity</td><td>""" + str(data['c_def_qty']) + """</td><td>""" + str(data['c_def_rate']) + """%</td><td>-</td></tr>
                    <tr><td>加工成本 | Processing Cost</td><td>-</td><td>""" + str(data.get('c_proc_pct', '-')) + """%</td><td>""" + str(data['c_proc_cost']) + """</td></tr>
                    <tr><td>總成本 | Total Cost</td><td>-</td><td>-</td><td>""" + str(data['c_total_cost']) + """</td></tr>
                    <tr class="highlight"><td>單顆成本 | Unit Cost</td><td>-</td><td>-</td><td>""" + str(data['c_unit_cost']) + """</td></tr>
                    <tr><td>目前售價 | Current Selling Price</td><td>-</td><td>-</td><td>""" + str(data['c_price']) + """ (""" + str(data.get('c_margin', '-')) + """%)</td></tr>
                </table>
            </div>
            <div class="section">
                <h2>評估：報價 | Evaluation: Quotation</h2>
                <table>
                    <tr><th>項目 | Item</th><th>數量 | Quantity</th><th>百分比 | Percentage</th><th>成本 (""" + str(data['currency']) + """) | Cost (""" + str(data['currency']) + """)</th></tr>
                    <tr><td>總投入數量 | Total Input Quantity</td><td>""" + str(data['e_total_qty']) + """</td><td>-</td><td>""" + str(data['e_total_input_cost']) + """</td></tr>
                    <tr><td>良品數量 | Good Product Quantity</td><td>""" + str(data['e_good_qty']) + """</td><td>""" + str(data['e_good_rate']) + """%</td><td>-</td></tr>
                    <tr><td>廢品數量 | Defective Quantity</td><td>""" + str(data['e_def_qty']) + """</td><td>""" + str(data['e_def_rate']) + """%</td><td>-</td></tr>
                    <tr><td>加工成本 | Processing Cost</td><td>-</td><td>""" + str(data.get('e_proc_pct', '-')) + """%</td><td>""" + str(data['e_proc_cost']) + """</td></tr>
                    <tr><td>總成本 | Total Cost</td><td>-</td><td>-</td><td>""" + str(data['e_total_cost']) + """</td></tr>
                    <tr class="highlight"><td>單顆成本 | Unit Cost</td><td>-</td><td>-</td><td>""" + str(data['e_unit_cost']) + """</td></tr>
                    <tr><td>建議售價 (毛利潤20%) | Suggested Selling Price (20% Profit Margin)</td><td>-</td><td>-</td><td>""" + str(data['e_suggest_price']) + """</td></tr>
                </table>
            </div>
        </div>
        <div class="process-section">
            <h2>工序比較 | Process Comparison</h2>
            <table>
                <tr><th>工序名稱 | Process Name</th><th>現況 (""" + str(data['currency']) + """) | Current Situation (""" + str(data['currency']) + """)</th><th>評估 (""" + str(data['currency']) + """) | Evaluation (""" + str(data['currency']) + """)</th></tr>
                """ + str(data['process_rows']) + """
            </table>
        </div>
        <div class="footer">
            Generated by 成本分析轉換工具
        </div>
    </body>
    </html>
    """
    return html_template

# --- 4. Streamlit 介面 ---
st.set_page_config(page_title="成本分析轉換工具", page_icon="💼", layout="wide")

st.markdown("""
    <style>
    .main { padding: 0; }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
    </style>
    """, unsafe_allow_html=True)

st.markdown("---")

# 美化標題和介紹
st.markdown("---")
st.markdown("### 📋 成本分析轉換工具")
st.markdown("上傳 Excel 檔案，智能解析成本數據並生成成本分析報表")

# 使用 4 欄分別放置不同的輸入項目
col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])

with col1:
    uploaded_file = st.file_uploader("📁 上傳 Excel 檔案", type=["xlsx", "csv"])

with col2:
    product_model = st.text_input("🏷️ 產品編號 *", placeholder="必填", help="例: 3-041004-032PN-0")

with col3:
    currency = st.selectbox("💱 幣別 *", ["-- 請選擇 --", "台幣 (NTD)", "美金 (USD)", "歐元 (EUR)", "澳幣 (AUD)", "英鎊 (GBP)"])

with col4:
    # 根據選擇的幣別設定預設匯率
    rate_defaults = {
        "台幣 (NTD)": 1.0,
        "美金 (USD)": 32.5,
        "歐元 (EUR)": 35.5,
        "澳幣 (AUD)": 21.5,
        "英鎊 (GBP)": 41.0
    }
    
    default_rate = rate_defaults.get(currency, 1.0) if currency != "-- 請選擇 --" else 1.0
    
    rate = st.number_input(
        "📊 匯率 *",
        value=default_rate,
        step=0.1,
        help="1 外幣 = ? 台幣"
    )

# 提取幣別代碼
if currency and currency != "-- 請選擇 --":
    currency_code = currency.split("(")[1].rstrip(")")
else:
    currency_code = None

# 驗證必填欄位
if uploaded_file:
    errors = []
    if not product_model.strip():
        errors.append("⚠️ 產品編號為必填項目")
    if not currency or currency == "-- 請選擇 --":
        errors.append("⚠️ 幣別為必填項目，請選擇")
    if rate <= 0:
        errors.append("⚠️ 匯率必須大於 0")
    
    if errors:
        for error in errors:
            st.error(error)
        st.stop()

if uploaded_file and product_model.strip() and currency and currency != "-- 請選擇 --" and rate > 0:
    # 讀取檔案
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    
    # 提取零件編號 (如果沒手動輸入的話)
    auto_part_no = str(df.iloc[1, 2]) if not df.empty else "Unknown"
    part_no = product_model if product_model else auto_part_no
    
    # 提取數據 (現況 vs 評估) - 先初始化所有鍵
    results = {
        "part_no": part_no,
        "currency": currency_code,
        "c_total_qty": get_val(df, "總投入數量", "current"),
        "c_good_qty": get_val(df, "良品數量", "current"),
        "c_def_qty": "-",
        "c_good_rate": "-",
        "c_def_rate": "-",
        "c_proc_pct": "-",
        "c_total_input_cost": get_val(df, "投入成本", "current", rate),
        "c_proc_cost": get_val(df, "加工成本", "current", rate),
        "c_total_cost": get_val(df, "總成本", "current", rate),
        "c_unit_cost": get_val(df, "單顆成本", "current", rate),
        "c_price": get_val(df, "目前售價", "current", rate),
        "c_margin": "-",
        
        "e_total_qty": get_val(df, "總投入數量", "eval"),
        "e_good_qty": get_val(df, "良品數量", "eval"),
        "e_def_qty": "-",
        "e_good_rate": "-",
        "e_def_rate": "-",
        "e_proc_pct": "-",
        "e_total_input_cost": get_val(df, "投入成本", "eval", rate),
        "e_proc_cost": get_val(df, "加工成本", "eval", rate),
        "e_total_cost": get_val(df, "總成本", "eval", rate),
        "e_unit_cost": get_val(df, "單顆成本", "eval", rate),
        "e_suggest_price": get_val(df, "建議售價", "eval", rate),
        "process_rows": "",
    }

    # 計算百分比 (設定預設值)
    results["c_def_qty"] = "-"
    results["c_good_rate"] = "-"
    results["c_def_rate"] = "-"
    results["c_margin"] = "-"
    results["e_def_qty"] = "-"
    results["e_good_rate"] = "-"
    results["e_def_rate"] = "-"
    
    try:
        if isinstance(results["c_total_qty"], (int, float)) and isinstance(results["c_good_qty"], (int, float)):
            results["c_def_qty"] = results["c_total_qty"] - results["c_good_qty"]
            results["c_good_rate"] = round((results["c_good_qty"] / results["c_total_qty"]) * 100, 2)
            results["c_def_rate"] = round(100 - results["c_good_rate"], 2)
        
        if isinstance(results["c_price"], (int, float)) and isinstance(results["c_unit_cost"], (int, float)) and results["c_unit_cost"] != 0:
            results["c_margin"] = round(((results["c_price"] - results["c_unit_cost"]) / results["c_unit_cost"]) * 100, 1)
        
        if isinstance(results["e_total_qty"], (int, float)) and isinstance(results["e_good_qty"], (int, float)):
            results["e_def_qty"] = results["e_total_qty"] - results["e_good_qty"]
            results["e_good_rate"] = round((results["e_good_qty"] / results["e_total_qty"]) * 100, 2)
            results["e_def_rate"] = round(100 - results["e_good_rate"], 2)
    except:
        pass

    # 處理工序列表 - 動態尋找所有工序
    process_html = ""
    
    # 尋找「製程」或「工序」標籤行
    proc_start_row = -1
    for i in range(len(df)):
        row_str = ' '.join([str(cell) for cell in df.iloc[i, :5]])
        if '製程' in row_str or '工序' in row_str:
            proc_start_row = i + 1
            break
    
    # 如果找不到標籤，從第 16 列開始
    if proc_start_row == -1:
        proc_start_row = 16
    
    # 從找到的位置開始提取所有工序
    for i in range(proc_start_row, len(df)):
        try:
            # 嘗試從第 1 列和第 2 列讀取工序名稱
            p_name = None
            for col_idx in [1, 2, 14, 15]:  # 檢查多個可能的欄位
                if col_idx < len(df.columns):
                    val = df.iloc[i, col_idx]
                    if pd.notna(val) and isinstance(val, str) and val.strip() and val not in ['製程', '工序', '']:
                        p_name = val.strip()
                        break
            
            if not p_name:
                # 如果沒找到名稱就停止
                if i > proc_start_row + 20:  # 至少往下看 20 列
                    break
                continue
            
            # 嘗試從不同欄位提取成本
            c_val = "-"
            e_val = "-"
            
            try:
                # 現況成本 - 嘗試第 7, 8, 9 欄
                for col_idx in [7, 8, 9]:
                    if col_idx < len(df.columns):
                        val = df.iloc[i, col_idx]
                        if pd.notna(val) and str(val).replace('.', '').replace('-', '').replace('e', '').replace('E', '').isdigit():
                            c_val = round(float(val) / rate, 2)
                            break
                
                # 評估成本 - 嘗試第 20, 21, 22 欄
                for col_idx in [20, 21, 22]:
                    if col_idx < len(df.columns):
                        val = df.iloc[i, col_idx]
                        if pd.notna(val) and str(val).replace('.', '').replace('-', '').replace('e', '').replace('E', '').isdigit():
                            e_val = round(float(val) / rate, 2)
                            break
            except:
                pass
            
            # 只有當至少有一個成本值時才加入
            if c_val != "-" or e_val != "-":
                c_val_formatted = format_price(c_val)
                e_val_formatted = format_price(e_val)
                process_html += f"<tr><td>{clean_process_name(p_name)}</td><td>{c_val_formatted}</td><td>{e_val_formatted}</td></tr>"
        
        except Exception as e:
            # 靜默跳過異常行
            continue
    
    results["process_rows"] = process_html

    # 格式化數據用於顯示
    display_data = {
        "part_no": results["part_no"],
        "currency": results["currency"],
        # 現況數量 - 整數
        "c_total_qty": format_quantity(results["c_total_qty"]),
        "c_good_qty": format_quantity(results["c_good_qty"]),
        "c_def_qty": format_quantity(results["c_def_qty"]),
        # 現況金額 - 3位小數
        "c_total_input_cost": format_price(results["c_total_input_cost"]),
        "c_proc_cost": format_price(results["c_proc_cost"]),
        "c_total_cost": format_price(results["c_total_cost"]),
        "c_unit_cost": format_price(results["c_unit_cost"]),
        "c_price": format_price(results["c_price"]),
        # 現況百分比
        "c_good_rate": results["c_good_rate"],
        "c_def_rate": results["c_def_rate"],
        "c_proc_pct": results.get("c_proc_pct", "-"),
        "c_margin": results["c_margin"],
        # 評估數量 - 整數
        "e_total_qty": format_quantity(results["e_total_qty"]),
        "e_good_qty": format_quantity(results["e_good_qty"]),
        "e_def_qty": format_quantity(results["e_def_qty"]),
        # 評估金額 - 3位小數
        "e_total_input_cost": format_price(results["e_total_input_cost"]),
        "e_proc_cost": format_price(results["e_proc_cost"]),
        "e_total_cost": format_price(results["e_total_cost"]),
        "e_unit_cost": format_price(results["e_unit_cost"]),
        "e_suggest_price": format_price(results["e_suggest_price"]),
        # 評估百分比
        "e_good_rate": results["e_good_rate"],
        "e_def_rate": results["e_def_rate"],
        "e_proc_pct": results.get("e_proc_pct", "-"),
        "process_rows": results["process_rows"]
    }

    # 生成 HTML
    final_html = generate_html(display_data)
    
    st.success(f"解析完成！料號：{part_no}")
    
    # 提供預覽與下載
    st.components.v1.html(final_html, height=600, scrolling=True)
    
    # 下載選項
    # HTML 下載
    b64 = base64.b64encode(final_html.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="Analysis_{part_no}.html">📄 下載 HTML</a>'
    st.markdown(href, unsafe_allow_html=True)
