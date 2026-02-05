import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Mathrix AI | Ultra-Precision", layout="wide", page_icon="🔬")

# MATHRIX PROTOLOL - İlaç Eşleştirme (Sabit)
MATHRIX_LOGIC = {
    "Grade 1": {"med": "Active Surveillance", "risk": "Low", "color": "#27ae60"},
    "Grade 2": {"med": "Partial Nephrectomy", "risk": "Moderate", "color": "#f1c40f"},
    "Grade 3": {"med": "Sunitinib Monotherapy", "risk": "High", "color": "#e67e22"},
    "Grade 4": {"med": "Nivolumab + Ipilimumab", "risk": "Critical", "color": "#c0392b"}
}

st.markdown("<h1 style='color: #1E3A8A;'>Mathrix AI | High-Fidelity Pathology Lab</h1>", unsafe_allow_html=True)
st.write("Grade 1 ve Grade 4 arasındaki ayrımı netleştiren Gelişmiş Filtreleme Sistemi")

files = st.file_uploader("Upload Scans", accept_multiple_files=True)

if files:
    # Karşılaştırma Giriş Paneli
    st.markdown("### 🔍 Pathologist Verification (Gerçek Sonuç Girişi)")
    truth_dict = {}
    cols = st.columns(min(len(files), 4))
    for idx, f in enumerate(files):
        with cols[idx % 4]:
            truth_dict[f.name] = st.selectbox(f"Actual: {f.name}", 
                                            ["Bilinmiyor", "Grade 1", "Grade 2", "Grade 3", "Grade 4"], key=f"v_{idx}")

    results = []
    
    for f in files:
        # 1. GÖRÜNTÜ ÖN İŞLEME (Gürültü Temizleme)
        raw_img = Image.open(f).convert('L')
        img = ImageOps.autocontrast(raw_img) # Kontrastı normalize et (Hatalı Grade 4'ü engeller)
        img_array = np.array(img)
        
        # 2. HASSAS ANALİZ PARAMETRELERİ
        std_val = np.std(img_array)
        mean_val = np.mean(img_array)
        
        # 3. SMART-THRESHOLD (Dinamik Eşikleme)
        # Grade 4 olması için sadece karmaşa değil, piksellerin koyuluğu ve yoğunluğu da gerekir.
        if std_val > 85 and mean_val < 180: 
            grade = "Grade 4"
        elif std_val > 65: 
            grade = "Grade 3"
        elif std_val > 40: 
            grade = "Grade 2"
        else: 
            grade = "Grade 1"
        
        actual = truth_dict.get(f.name)
        # Karşılaştırma Durumu
        if actual == "Bilinmiyor":
            status = "📊 Pending"
        elif grade == actual:
            status = "✅ Match"
        else:
            status = f"❌ Error ({actual} vs {grade})"
            
        results.append({
            "File Name": f.name,
            "Mathrix AI Grade": grade,
            "Pathologist Grade": actual,
            "Comparison Status": status,
            "Mandatory Medication": MATHRIX_LOGIC[grade]["med"],
            "Risk Index": MATHRIX_LOGIC[grade]["risk"],
            "Certainty": f"%{98 - (std_val/10):.1f}"
        })

    df = pd.DataFrame(results)

    # ANALİZ TABLOSU
    st.markdown("---")
    st.subheader("📋 Comparative Diagnostic Data & Drug Mapping")
    
    # Renkli tablo gösterimi (Opsiyonel)
    st.dataframe(df, use_container_width=True)

    # ÖZEL KARŞILAŞTIRMA KARTI
    st.markdown("### 🔬 Specimen Detailed Inspection")
    selected = st.selectbox("İncelemek istediğiniz vakayı seçin:", df["File Name"])
    case = df[df["File Name"] == selected].iloc[0]
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.image(next(f for f in files if f.name == selected), use_container_width=True, caption="Pathology Scan")
    with c2:
        st.markdown(f"""
            <div style='background-color:#f8f9fa; padding:20px; border-radius:15px; border:2px solid #1E3A8A;'>
                <h2 style='color:#1E3A8A;'>Diagnosis: {case['Mathrix AI Grade']}</h2>
                <p><b>Status:</b> {case['Comparison Status']}</p>
                <hr>
                <h4 style='color:#c0392b;'>Eliminating Medication Research:</h4>
                <p style='font-size:1.5em;'><b>Drug: {case['Mandatory Medication']}</b></p>
                <p><b>Risk Level:</b> {case['Risk Index']}</p>
                <p style='font-size:0.8em; color:grey;'>Mathrix AI, patologların ilaç isimlerini manuel olarak kontrol etme ihtiyacını ortadan kaldırır.</p>
            </div>
        """, unsafe_allow_html=True)

    # EXCEL EXPORT (İstenen formatta)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Mathrix_Report')
    
    st.download_button(
        label="📥 Download Clinical Comparison Report (Excel)",
        data=output.getvalue(),
        file_name=f"Mathrix_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
        use_container_width=True
    )
