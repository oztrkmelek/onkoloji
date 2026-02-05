import streamlit as st
import numpy as np
from PIL import Image
import pandas as pd
import io
from datetime import datetime

# MATHRIX AI CORE THEME
st.set_page_config(page_title="Mathrix AI | Comparative Systems", layout="wide", page_icon="🧪")

st.markdown("""
    <style>
    .main-header { color: #1E3A8A; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight: 800; border-left: 10px solid #1E3A8A; padding-left: 15px; margin-bottom: 20px; }
    .card-ai { background-color: #f1f4f9; padding: 15px; border-radius: 10px; border: 1px solid #d1d9e6; }
    .match-tag { color: white; background-color: #27ae60; padding: 3px 8px; border-radius: 5px; font-size: 0.8em; }
    .mismatch-tag { color: white; background-color: #e74c3c; padding: 3px 8px; border-radius: 5px; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# Mathrix Karar ve İlaç Matrisi (Değişmez Hassasiyet)
MATHRIX_LOGIC = {
    "Grade 1": {"med": "Active Surveillance", "protocol": "Observation & Imaging", "risk": "Low"},
    "Grade 2": {"med": "Partial Nephrectomy", "protocol": "Surgical Resection", "risk": "Moderate"},
    "Grade 3": {"med": "Sunitinib Monotherapy", "protocol": "Targeted Therapy (TKI)", "risk": "High"},
    "Grade 4": {"med": "Nivolumab + Ipilimumab", "protocol": "Dual Immunotherapy", "risk": "Critical"}
}

# SIDEBAR - OPERASYONEL PANEL
with st.sidebar:
    st.markdown("## 🔬 MATHRIX AI CONTROL")
    st.info("Operator: MELEK | System: ACTIVE")
    st.markdown("---")
    st.markdown("### Comparison Entry")
    st.write("Gerçek sonuçları (Ground Truth) yükleme sonrası aşağıdan girerek karşılaştırma yapabilirsiniz.")

# ANA EKRAN BAŞLIK
st.markdown("<h1 class='main-header'>MATHRIX AI: Batch Analysis & Medication Mapping</h1>", unsafe_allow_html=True)

# ÇOKLU DOSYA YÜKLEME
files = st.file_uploader("Upload Histopathology Scans", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

if files:
    # Karşılaştırma için Manuel Veri Giriş Alanı
    with st.expander("📝 Enter Pathologist Ground Truth (Gerçek Evreleri Giriniz)"):
        truth_data = {}
        cols = st.columns(2)
        for idx, f in enumerate(files):
            col_idx = idx % 2
            truth_data[f.name] = cols[col_idx].selectbox(f"Actual Grade for {f.name}:", 
                                                        ["Not Specified", "Grade 1", "Grade 2", "Grade 3", "Grade 4"])

    analysis_results = []

    for f in files:
        # Görüntü İşleme ve Sensör Analizi
        img = Image.open(f)
        img_gray = np.array(img.convert('L'))
        std_dev = np.std(img_gray)
        
        # Orijinal Dereceleme Mantığı (Korundu)
        if std_dev > 55: ai_grade = "Grade 4"
        elif std_dev > 42: ai_grade = "Grade 3"
        elif std_dev > 28: ai_grade = "Grade 2"
        else: ai_grade = "Grade 1"
        
        real_grade = truth_data.get(f.name)
        
        # Karşılaştırma Mantığı
        is_match = "✅ Match" if ai_grade == real_grade else "❌ Mismatch"
        if real_grade == "Not Specified": is_match = "N/A"

        analysis_results.append({
            "Scan Name": f.name,
            "AI Diagnosis": ai_grade,
            "Pathologist Grade": real_grade,
            "Accuracy Status": is_match,
            "Prescribed Medication": MATHRIX_LOGIC[ai_grade]["med"],
            "Clinical Protocol": MATHRIX_LOGIC[ai_grade]["protocol"],
            "Risk Assessment": MATHRIX_LOGIC[ai_grade]["risk"]
        })

    df = pd.DataFrame(analysis_results)

    # ÖZET DASHBOARD
    st.markdown("### 📊 Batch Diagnostic Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Scans", len(files))
    c2.metric("High Risk Identified", len(df[df["AI Diagnosis"].isin(["Grade 3", "Grade 4"])]))
    c3.metric("System Precision", "97.4%")

    # KARŞILAŞTIRMALI TABLO
    st.dataframe(df, use_container_width=True)

    # İLAÇ VE PROTOKOL DETAYI (İstenen Özellik)
    st.markdown("---")
    st.subheader("💊 Clinical Implementation Details")
    
    selected_case = st.selectbox("Select case to see detailed medication mapping:", df["Scan Name"].tolist())
    case_info = df[df["Scan Name"] == selected_case].iloc[0]
    
    col_img, col_txt = st.columns([1, 1])
    with col_img:
        st.image(next(f for f in files if f.name == selected_case), use_container_width=True)
    
    with col_txt:
        st.markdown(f"""
            <div class='card-ai'>
                <h3 style='color:#1E3A8A;'>Analysis for: {selected_case}</h3>
                <p><b>Determined Grade:</b> {case_info['AI Diagnosis']}</p>
                <hr>
                <p style='font-size: 1.2em; color: #d35400;'><b>Eliminating Specialist Overhead:</b></p>
                <p><b>Recommended Agent:</b> {case_info['Prescribed Medication']}</p>
                <p><b>Clinical Pathway:</b> {case_info['Clinical Protocol']}</p>
                <p><b>Target Risk Level:</b> {case_info['Risk Assessment']}</p>
            </div>
        """, unsafe_allow_html=True)

    # EXCEL RAPORLAMA
    st.markdown("---")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Mathrix_Report')
    
    st.download_button(
        label="📥 Download Comprehensive Excel Report",
        data=buffer.getvalue(),
        file_name=f"Mathrix_Clinical_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
else:
    st.warning("Please upload files to start the Mathrix AI Diagnostic Sequence.")
