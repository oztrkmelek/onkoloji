import streamlit as st
import numpy as np
from PIL import Image
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Mathrix AI | Precision Systems", layout="wide", page_icon="🔬")

# MATHRIX LOGIC - Sabit İlaç Rehberi
MATHRIX_LOGIC = {
    "Grade 1": {"med": "Active Surveillance", "risk": "Low", "desc": "Uniform nuclei, no nucleoli"},
    "Grade 2": {"med": "Partial Nephrectomy", "risk": "Moderate", "desc": "Slightly irregular nuclei"},
    "Grade 3": {"med": "Sunitinib Monotherapy", "risk": "High", "desc": "Prominent nucleoli at 10x"},
    "Grade 4": {"med": "Nivolumab + Ipilimumab", "risk": "Critical", "desc": "Extreme pleomorphism / Giant cells"}
}

st.markdown("<h1 style='color: #1E3A8A;'>Mathrix AI | Balanced Batch Analysis</h1>", unsafe_allow_html=True)

uploaded_files = st.file_uploader("Upload Pathology Scans", accept_multiple_files=True)

if uploaded_files:
    # Karşılaştırma için manuel giriş alanı
    st.markdown("### 📋 Pathologist Verification")
    truth_dict = {}
    t_cols = st.columns(len(uploaded_files) if len(uploaded_files) < 5 else 5)
    for idx, f in enumerate(uploaded_files):
        with t_cols[idx % 5]:
            truth_dict[f.name] = st.selectbox(f"Actual: {f.name[:10]}...", 
                                            ["N/A", "Grade 1", "Grade 2", "Grade 3", "Grade 4"], key=f"truth_{idx}")

    results = []
    
    for f in uploaded_files:
        img = Image.open(f).convert('L')
        img_array = np.array(img)
        
        # Hata payını azaltmak için ham değer yerine varyasyonu hesaplıyoruz
        # Grade 4 demesini zorlaştırmak için limitleri güncelledik
        std_val = np.std(img_array)
        
        # YENİLENMİŞ HASSAS EŞİKLER (Grade 4'e yığılmayı önlemek için limitler artırıldı)
        if std_val > 75: 
            grade = "Grade 4"
        elif std_val > 60: 
            grade = "Grade 3"
        elif std_val > 45: 
            grade = "Grade 2"
        else: 
            grade = "Grade 1"
        
        actual = truth_dict.get(f.name)
        match_status = "✅ Match" if grade == actual else "⚠️ Mismatch" if actual != "N/A" else "Pending"
        
        results.append({
            "Case ID": f.name,
            "AI Grade": grade,
            "Actual Grade": actual,
            "Comparison": match_status,
            "Targeted Medication": MATHRIX_LOGIC[grade]["med"],
            "Risk Index": MATHRIX_LOGIC[grade]["risk"],
            "Sensor Value": round(std_val, 2) # Neden Grade 4 dediğini görmek için teknik değer
        })

    df = pd.DataFrame(results)

    # DASHBOARD
    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Cases", len(uploaded_files))
    m2.metric("Accuracy Rate", f"%{ (len(df[df['Comparison']=='✅ Match']) / len(df) * 100) if '✅ Match' in df['Comparison'].values else 0:.1f}")
    m3.write("*Sensor Info:* Higher values = Higher Grade")

    # KARŞILAŞTIRMALI TABLO
    st.subheader("📊 Comparative Results & Medication Mapping")
    st.dataframe(df, use_container_width=True)

    # EXCEL DOWNLOAD
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button("📥 Download Excel Report", output.getvalue(), 
                       file_name="Mathrix_Comparison.xlsx", use_container_width=True)

else:
    st.info("Sistemi başlatmak için görüntü yükleyin. Grade 4 yoğunluğu varsa sensör değerlerini (std_val) kontrol ediniz.")
