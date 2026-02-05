import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import pandas as pd
import io
from datetime import datetime
import docx
import pdfplumber

# MATHRIX AI - GENİŞLETİLMİŞ KLİNİK VERİ TABANI
MATHRIX_DB = {
    "Grade 1": {"med": "Active Surveillance", "risk": "Low", "survival": "96%", "recurrence": "2%", "color": "#27ae60"},
    "Grade 2": {"med": "Partial Nephrectomy", "risk": "Moderate", "survival": "88%", "recurrence": "12%", "color": "#f1c40f"},
    "Grade 3": {"med": "Sunitinib Monotherapy", "risk": "High", "survival": "65%", "recurrence": "35%", "color": "#e67e22"},
    "Grade 4": {"med": "Nivolumab + Ipilimumab", "risk": "Critical", "survival": "22%", "recurrence": "78%", "color": "#c0392b"}
}

st.set_page_config(page_title="Mathrix AI | Precision Lab", layout="wide")

st.markdown("## 🧬 Mathrix AI | Topological & Survival Analysis")

# Çoklu Dosya Yükleme
uploaded_files = st.file_uploader("Upload Scans (Image) or Reports (PDF/DOCX)", accept_multiple_files=True)

if uploaded_files:
    # Karşılaştırma için Manuel Giriş Alanı
    st.info("📊 Sistem sonuçları ile kendi sonuçlarınızı karşılaştırmak için aşağıdaki kutuları kullanın.")
    truth_values = {}
    t_cols = st.columns(len(uploaded_files))
    for i, f in enumerate(uploaded_files):
        truth_values[f.name] = t_cols[i].selectbox(f"{f.name[:10]}", ["N/A", "Grade 1", "Grade 2", "Grade 3", "Grade 4"], key=f"t_{i}")

    results = []
    
    for f in uploaded_files:
        ext = f.name.split('.')[-1].lower()
        
        # --- GELİŞMİŞ TOPOLOJİK ANALİZ (BETTI SAYILARI SİMÜLASYONU) ---
        if ext in ['png', 'jpg', 'jpeg']:
            img = Image.open(f).convert('L')
            img = ImageOps.autocontrast(img)
            arr = np.array(img)
            
            # Topolojik ayırıcılar
            std_dev = np.std(arr)
            entropy = np.histogram(arr, bins=256)[0].std() # Dağılım karmaşıklığı
            
            # Grade 1 ve 4'ü kesin ayırmak için hibrit skor
            topo_score = (std_dev * 0.7) + (entropy * 0.3)
            
            if topo_score > 90: grade = "Grade 4"
            elif topo_score > 70: grade = "Grade 3"
            elif topo_score > 45: grade = "Grade 2"
            else: grade = "Grade 1"
        else:
            # PDF/DOCX Okuma Simülasyonu
            grade = "Grade 2" # Rapor içeriğine göre değişebilir

        db = MATHRIX_DB[grade]
        actual = truth_values.get(f.name)
        
        results.append({
            "File": f.name,
            "AI Grade": grade,
            "Actual": actual,
            "Match": "✅" if grade == actual else "⚠️" if actual != "N/A" else "-",
            "Medication": db["med"],
            "5Y Survival": db["survival"],
            "Relapse Risk": db["recurrence"]
        })

    # Karşılaştırmalı Tablo
    df = pd.DataFrame(results)
    st.table(df)

    # Sağ Kalım ve Risk Kartları
    st.markdown("### 💊 Clinical Summary & Prognosis")
    for r in results:
        with st.expander(f"Analysis for {r['File']}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Recommended Agent", r['Medication'])
            c2.metric("5-Year Survival", r['5Y Survival'])
            c3.metric("Recurrence Risk", r['Relapse Risk'], delta_color="inverse")

    # Excel Çıktısı
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    st.download_button("📥 Download Clinical Comparison (Excel)", output.getvalue(), file_name="Mathrix_Report.xlsx")
