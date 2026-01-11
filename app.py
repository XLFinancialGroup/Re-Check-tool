import streamlit as st
import os
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(
    page_title="Actuarial Governance Re-Check", 
    page_icon="🛡️", 
    layout="wide"
)

# Initialize Session State for persistence
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'total_score' not in st.session_state:
    st.session_state.total_score = 0

# Logo Helper
def render_logo():
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", use_container_width=True)
    else:
        st.sidebar.markdown("### 🛡️ Xu Consulting Group")

# ==========================================
# 2. Text Database
# ==========================================
UI_TEXT = {
    'English': {
        'title': "Actuarial Governance Re-Check",
        'subtitle': "Peak Re / Big4 Style Diagnostic Tool",
        'lang_select': "Language / 语言",
        'module_a': "Module A: Data Quality & Lineage",
        'module_b': "Module B: Reserving & Governance",
        'calc_btn': "📊 Run Diagnostic Assessment",
        'result_header': "Assessment Dashboard",
        'score_label': "Governance Score",
        'risk_label': "Risk Rating",
        'contact': "Book Expert Review",
        'download': "📥 Download PDF Report"
    },
    '简体中文': {
        'title': "再保险精算合规体检系统",
        'subtitle': "基于行业最佳实践的治理评估工具",
        'lang_select': "选择语言",
        'module_a': "模块 A: 数据质量与连结",
        'module_b': "模块 B: 准备金与管理",
        'calc_btn': "📊 生成诊断仪表盘",
        'result_header': "诊断结果仪表盘",
        'score_label': "合规治理得分",
        'risk_label': "风险评级",
        'contact': "预约专家解读",
        'download': "📥 下载 PDF 报告"
    },
    '繁體中文': {
        'title': "再保險精算合規體檢系統",
        'subtitle': "基於行業最佳實踐的治理評估工具",
        'lang_select': "選擇語言",
        'module_a': "模塊 A: 數據質量與連結",
        'module_b': "模塊 B: 準備金與管理",
        'calc_btn': "📊 生成診斷儀表盤",
        'result_header': "診斷結果儀表盤",
        'score_label': "合規治理得分",
        'risk_label': "風險評級",
        'contact': "預約專家解讀",
        'download': "📥 下載 PDF 報告"
    }
}

QUESTIONS = [
    # --- Module A ---
    {"id": "DQ1", "scores": [0, 5, 10], "text": {"English": "Data Automation Level", "简体中文": "数据自动化程度", "繁體中文": "數據自動化程度"}, 
     "options": {"English": ["Manual", "Semi-Auto", "Fully Auto"], "简体中文": ["手动", "半自动", "全自动"], "繁體中文": ["手動", "半自動", "全自動"]}},
    {"id": "DQ2", "scores": [0, 5, 10], "text": {"English": "Cedant Data Validation", "简体中文": "分出方数据验证", "繁體中文": "分出方數據驗證"}, 
     "options": {"English": ["Passive", "Reactive", "Proactive"], "简体中文": ["被动", "反应式", "主动式"], "繁體中文": ["被動", "反應式", "主動式"]}},
    {"id": "DQ3", "scores": [0, 5, 10], "text": {"English": "Data Lineage Map", "简体中文": "数据血缘地图", "繁體中文": "數據血緣地圖"}, 
     "options": {"English": ["None", "Partial", "Documented"], "简体中文": ["无", "部分", "文档齐全"], "繁體中文": ["無", "部分", "文檔齊全"]}},
    {"id": "DQ4", "scores": [0, 5, 10], "text": {"English": "Reconciliation Frequency", "简体中文": "对账频率", "繁體中文": "對賬頻率"}, 
     "options": {"English": ["Annual", "Quarterly", "Monthly"], "简体中文": ["年度", "季度", "月度"], "繁體中文": ["年度", "季度", "月度"]}},
    {"id": "DQ5", "scores": [0, 5, 10], "text": {"English": "Manual Adjustment Log", "简体中文": "手动调整日志", "繁體中文": "手動調整日誌"}, 
     "options": {"English": ["Excel", "Folder", "System Log"], "简体中文": ["Excel记录", "文件夹归档", "系统日志"], "繁體中文": ["Excel記錄", "文件夾歸檔", "系統日誌"]}},
    
    # --- Module B ---
    {"id": "RS1", "scores": [0, 5, 10], "text": {"English": "Independent Review", "简体中文": "独立审查机制", "繁體中文": "獨立審查機制"}, 
     "options": {"English": ["Internal", "Audit", "External"], "简体中文": ["仅内部", "内部审计", "外部独立"], "繁體中文": ["僅內部", "內部審計", "外部獨立"]}},
    {"id": "RS2", "scores": [0, 5, 10], "text": {"English": "IFRS 17 AoC Insight", "简体中文": "IFRS 17 变动分析深度", "繁體中文": "IFRS 17 變動分析深度"}, 
     "options": {"English": ["Black Box", "Compliance", "Strategic"], "简体中文": ["黑盒", "合规达标", "战略洞察"], "繁體中文": ["黑盒", "合規達標", "戰略洞察"]}},
    {"id": "RS3", "scores": [0, 5, 10], "text": {"English": "Sensitivity Speed", "简体中文": "敏感性分析速度", "繁體中文": "敏感性分析速度"}, 
     "options": {"English": ["Weeks", "Days", "Real-time"], "简体中文": ["数周", "数天", "实时"], "繁體中文": ["數周", "數天", "實時"]}},
    {"id": "RS4", "scores": [0, 5, 10], "text": {"English": "Pricing Feedback Loop", "简体中文": "定价反馈闭环", "繁體中文": "定價反饋閉環"}, 
     "options": {"English": ["None", "Ad-hoc", "Integrated"], "简体中文": ["无", "临时", "集成闭环"], "繁體中文": ["無", "臨時", "集成閉環"]}},
    {"id": "RS5", "scores": [0, 5, 10], "text": {"English": "Methodology Change Doc", "简体中文": "变更文档规范", "繁體中文": "變更文檔規範"}, 
     "options": {"English": ["Email", "Notes", "Formal Memo"], "简体中文": ["邮件", "笔记", "正式备忘"], "繁體中文": ["郵件", "筆記", "正式備忘"]}},
]

# ==========================================
# 3. PDF Generator Function
# ==========================================
def generate_pdf_report(score, risk_text, lang_code):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Default Font
    selected_font = "Helvetica"
    font_file = None

    # Determine Font file based on language
    if lang_code == "简体中文":
        font_file = "font_sc.ttf"
        custom_font_name = "CustomSC"
    elif lang_code == "繁體中文":
        font_file = "font_tc.ttf"
        custom_font_name = "CustomTC"
    
    # Try to register font if file exists
    used_lang_mode = "English" # Default to English mode if fonts fail
    if font_file and os.path.exists(font_file):
        try:
            pdfmetrics.registerFont(TTFont(custom_font_name, font_file))
            selected_font = custom_font_name
            used_lang_mode = lang_code
        except Exception:
            pass # Fail silently back to Helvetica

    # --- Draw Content ---
    c.setFont(selected_font, 24)
    
    # Title
    if used_lang_mode == "简体中文":
        title = "再保险精算合规体检报告"
    elif used_lang_mode == "繁體中文":
        title = "再保險精算合規體檢報告"
    else:
        title = "Actuarial Governance Re-Check"
    
    c.drawString(50, height - 80, title)
    c.line(50, height - 100, 550, height - 100)

    # Score
    c.setFont(selected_font, 18)
    c.drawString(50, height - 150, f"Score: {score} / 100")
    
    # Risk (Handle potential encoding issues if font missing)
    if used_lang_mode == "English" and lang_code != "English":
         c.drawString(50, height - 180, f"Risk Rating: {score} (Font missing, showing numeric)")
    else:
         c.drawString(50, height - 180, f"Risk Rating: {risk_text}")

    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(50, 50, "Powered by Xu Consulting Group | Confidential")

    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# 4. Main Interface Logic
# ==========================================

# --- Sidebar ---
render_logo()
st.sidebar.markdown("---")
st.sidebar.title("⚙️ " + UI_TEXT['English']['lang_select'].split('/')[0])
lang = st.sidebar.selectbox("", ["English", "简体中文", "繁體中文"], label_visibility="collapsed")
t = UI_TEXT[lang]

# --- Main Content ---
st.title("🛡️ " + t['title'])
st.caption(f"**Xu Consulting Group** | {t['subtitle']}")
st.markdown("---")

col_a, col_b = st.columns(2, gap="large")
temp_score = 0

# Left Col: Module A
with col_a:
    st.subheader(f"📂 {t['module_a']}")
    for q in QUESTIONS[:5]:
        st.markdown(f"**{q['text'][lang]}**")
        sel = st.radio(f"Label_{q['id']}", [0, 1, 2], format_func=lambda x: q['options'][lang][x], key=q['id'], label_visibility="collapsed", horizontal=True)
        temp_score += q['scores'][sel]
        st.write("")

# Right Col: Module B
with col_b:
    st.subheader(f"⚖️ {t['module_b']}")
    for q in QUESTIONS[5:]:
        st.markdown(f"**{q['text'][lang]}**")
        sel = st.radio(f"Label_{q['id']}", [0, 1, 2], format_func=lambda x: q['options'][lang][x], key=q['id'], label_visibility="collapsed", horizontal=True)
        temp_score += q['scores'][sel]
        st.write("")

st.markdown("---")

# ==========================================
# 5. Dashboard & PDF Trigger
# ==========================================

if st.button(t['calc_btn'], type="primary", use_container_width=True):
    st.session_state.show_results = True
    st.session_state.total_score = temp_score

if st.session_state.show_results:
    final_score = st.session_state.total_score
    
    st.markdown(f"### 📈 {t['result_header']}")
    
    # Risk Logic
    if final_score < 50:
        color = "red"
        risk_text = "HIGH RISK (高风险)" if lang == 'English' else "高风险 (High Risk)"
        risk_icon = "🔴"
    elif final_score < 80:
        color = "orange"
        risk_text = "MODERATE (中等风险)" if lang == 'English' else "中等风险 (Moderate)"
        risk_icon = "🟡"
    else:
        color = "green"
        risk_text = "LOW RISK (低风险)" if lang == 'English' else "低风险 (Low Risk)"
        risk_icon = "🟢"

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label=t['score_label'], value=f"{final_score} / 100")
    with m2:
        st.metric(label=t['risk_label'], value=risk_text)
    with m3:
        st.write("Governance Health")
        st.progress(final_score / 100)
    
    st.markdown("---")
    
    # Risk Commentary
    if color == "red":
        st.error(f"#### {risk_icon} Critical Attention Required")
        if lang == "English":
            st.write("Your governance structure shows significant gaps. **Process gaps are likely hidden.**")
        else:
            st.write("您的治理结构显示出重大漏洞。**流程缺陷可能非常隐蔽。**")
    elif color == "orange":
        st.warning(f"#### {risk_icon} Operational Efficiency Warning")
        if lang == "English":
             st.write("Basic compliance met, but manual processes create operational risks.")
        else:
             st.write("已满足基本合规，但人工流程带来了操作风险。")
    else:
        st.success(f"#### {risk_icon} Industry Leader")
        st.write("Excellent baseline.")

    # Contact
    st.info(f"👉 **{t['contact']}:** James.Xu@xuconsultinggroup.com")

    # --- PDF Download Button ---
    pdf_data = generate_pdf_report(final_score, risk_text, lang)
    
    st.download_button(
        label=t['download'],
        data=pdf_data,
        file_name=f"Governance_Report_{final_score}.pdf",
        mime="application/pdf",
        type="secondary"
    )