import streamlit as st
import os
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ==========================================
# 1. 页面配置
# ==========================================
st.set_page_config(
    page_title="Actuarial Governance Re-Check", 
    page_icon="🛡️", 
    layout="wide"
)

# 初始化 Session State
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'total_score' not in st.session_state:
    st.session_state.total_score = 0
if 'user_selections' not in st.session_state:
    st.session_state.user_selections = {} # 新增：用于存储用户的具体选择

def render_logo():
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", use_container_width=True)
    else:
        st.sidebar.markdown("### 🛡️ Xu Consulting Group")

# ==========================================
# 2. 文本数据库 (保持不变)
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
        'download': "📥 Download Detailed Report (PDF)",
        'pdf_title': "Governance Diagnostic Report",
        'detail_section': "Diagnostic Details"
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
        'download': "📥 下载详细诊断报告 (PDF)",
        'pdf_title': "精算治理诊断报告",
        'detail_section': "诊断明细"
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
        'download': "📥 下載詳細診斷報告 (PDF)",
        'pdf_title': "精算治理診斷報告",
        'detail_section': "診斷明細"
    }
}

QUESTIONS = [
    # --- Module A ---
    {"id": "DQ1", "scores": [0, 5, 10], "text": {"English": "Data Automation Level", "简体中文": "数据自动化程度", "繁體中文": "數據自動化程度"}, 
     "options": {"English": ["Manual (High Risk)", "Semi-Auto", "Fully Auto"], "简体中文": ["手动 (高风险)", "半自动", "全自动"], "繁體中文": ["手動 (高風險)", "半自動", "全自動"]}},
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
# 3. 升级版 PDF 生成器 (支持多页和表格化布局)
# ==========================================
def generate_detailed_pdf(score, risk_text, lang_code, user_selections):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # --- 字体处理 ---
    selected_font = "Helvetica"
    selected_font_bold = "Helvetica-Bold"
    font_file = None
    custom_font_name = "CustomFont"

    if lang_code == "简体中文":
        font_file = "font_sc.ttf"
    elif lang_code == "繁體中文":
        font_file = "font_tc.ttf"
    
    used_lang_mode = "English" 
    if font_file and os.path.exists(font_file):
        try:
            pdfmetrics.registerFont(TTFont(custom_font_name, font_file))
            selected_font = custom_font_name
            selected_font_bold = custom_font_name # 简化处理，粗体也用如同一个字体
            used_lang_mode = lang_code
        except Exception:
            pass 

    # --- 辅助函数：绘制页眉 ---
    def draw_header(c, y_pos):
        # 顶部深色条
        c.setFillColorRGB(0.1, 0.2, 0.4) # 深蓝色
        c.rect(0, height - 80, width, 80, fill=1, stroke=0)
        
        c.setFillColor(colors.white)
        c.setFont(selected_font_bold, 24)
        
        title = UI_TEXT[lang_code]['pdf_title'] if used_lang_mode != "English" else UI_TEXT['English']['pdf_title']
        c.drawString(40, height - 50, title)
        
        c.setFont(selected_font, 10)
        c.drawString(40, height - 70, "Xu Consulting Group | Confidential Assessment")
        
        # 恢复黑色字体
        c.setFillColor(colors.black)
        return height - 120

    # --- 开始绘制 ---
    y = draw_header(c, height)

    # 1. 摘要部分
    c.setFont(selected_font_bold, 16)
    c.drawString(40, y, f"Executive Summary (摘要)")
    y -= 30
    
    c.setFont(selected_font, 12)
    c.drawString(40, y, f"Total Governance Score: {score} / 100")
    c.drawString(300, y, f"Risk Rating: {risk_text}")
    
    # 绘制简单的进度条可视化
    y -= 30
    c.setStrokeColor(colors.grey)
    c.rect(40, y, 400, 15, stroke=1, fill=0) # 背景框
    
    bar_color = colors.green if score >= 80 else (colors.orange if score >= 50 else colors.red)
    c.setFillColor(bar_color)
    c.rect(40, y, 400 * (score/100), 15, stroke=0, fill=1) # 进度条
    
    y -= 40
    c.setFillColor(colors.black)
    c.line(40, y, 550, y) # 分割线
    y -= 30

    # 2. 详细问答部分
    c.setFont(selected_font_bold, 14)
    section_title = UI_TEXT[lang_code]['detail_section'] if used_lang_mode != "English" else UI_TEXT['English']['detail_section']
    c.drawString(40, y, section_title)
    y -= 30

    c.setFont(selected_font, 10)
    
    # 遍历所有问题并打印
    for index, q in enumerate(QUESTIONS):
        # 检查是否需要换页
        if y < 80:
            c.showPage() # 新建一页
            y = draw_header(c, height) # 重新画页眉
            c.setFont(selected_font, 10)

        # 获取用户选择
        user_sel_idx = user_selections.get(q['id'], 0) # 默认为0
        sel_text = q['options'][lang_code][user_sel_idx]
        score_val = q['scores'][user_sel_idx]
        
        # 问题标题
        q_text = q['text'][lang_code]
        c.setFont(selected_font_bold, 11)
        c.drawString(40, y, f"Q{index+1}: {q_text}")
        
        # 用户回答
        c.setFont(selected_font, 10)
        # 如果分数低，用红色标记
        if score_val == 0:
            c.setFillColor(colors.red)
        elif score_val == 5:
            c.setFillColorRGB(0.8, 0.4, 0) # Orange-ish
        else:
            c.setFillColor(colors.black)
            
        c.drawString(60, y - 15, f"• Selected: {sel_text} (+{score_val} pts)")
        
        c.setFillColor(colors.black)
        y -= 40 # 下移一行

    # 底部版权
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.grey)
    c.drawString(40, 30, "Generated by Streamlit • Xu Consulting Group")

    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# 4. 主界面逻辑
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

# 临时变量，用于本次运行计算
current_run_score = 0
current_run_selections = {}

# 左栏：Module A
with col_a:
    st.subheader(f"📂 {t['module_a']}")
    for q in QUESTIONS[:5]:
        st.markdown(f"**{q['text'][lang]}**")
        # Radio 默认值逻辑可以优化，这里简化处理
        sel = st.radio(f"Label_{q['id']}", [0, 1, 2], format_func=lambda x: q['options'][lang][x], key=q['id'], label_visibility="collapsed", horizontal=True)
        current_run_score += q['scores'][sel]
        current_run_selections[q['id']] = sel # 记录选择
        st.write("")

# 右栏：Module B
with col_b:
    st.subheader(f"⚖️ {t['module_b']}")
    for q in QUESTIONS[5:]:
        st.markdown(f"**{q['text'][lang]}**")
        sel = st.radio(f"Label_{q['id']}", [0, 1, 2], format_func=lambda x: q['options'][lang][x], key=q['id'], label_visibility="collapsed", horizontal=True)
        current_run_score += q['scores'][sel]
        current_run_selections[q['id']] = sel # 记录选择
        st.write("")

st.markdown("---")

# ==========================================
# 5. 结果与 PDF
# ==========================================

if st.button(t['calc_btn'], type="primary", use_container_width=True):
    st.session_state.show_results = True
    st.session_state.total_score = current_run_score
    st.session_state.user_selections = current_run_selections # 保存用户的具体选项到 Session

if st.session_state.show_results:
    final_score = st.session_state.total_score
    
    st.markdown(f"### 📈 {t['result_header']}")
    
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
    
    if color == "red":
        st.error(f"#### {risk_icon} Critical Attention Required")
        st.write(f"Risk Rating: {risk_text}")
    elif color == "orange":
        st.warning(f"#### {risk_icon} Operational Efficiency Warning")
        st.write(f"Risk Rating: {risk_text}")
    else:
        st.success(f"#### {risk_icon} Industry Leader")
        st.write(f"Risk Rating: {risk_text}")

    st.info(f"👉 **{t['contact']}:** James.Xu@xuconsultinggroup.com")

    # --- 生成详细版 PDF ---
    # 传入 score, risk_text, lang, 以及最重要的 user_selections
    pdf_data = generate_detailed_pdf(
        final_score, 
        risk_text, 
        lang, 
        st.session_state.user_selections
    )
    
    st.download_button(
        label=t['download'],
        data=pdf_data,
        file_name=f"Detailed_Report_{final_score}.pdf",
        mime="application/pdf",
        type="primary" # 样式改为主要按钮，更显眼
    )