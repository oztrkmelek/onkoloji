import streamlit as st
import numpy as np
import pandas as pd
import io
from PIL import Image
from skimage import color, feature, filters, util

# --- Clinical Intelligence Database (2025-2026 NCCN/EAU Guidelines) ---
CLINICAL_GUIDELINES = {
    "Grade 1": {
        "Diagnosis": "Stage I / Low-Grade Localized RCC",
        "Survival": "5-Year Overall Survival: ~95% | Progression-Free Survival (PFS): High",
        "Treatment": "Nephron-Sparing Surgery (Partial Nephrectomy) preferred for tumors <= 4cm (T1a).",
        "Adjuvant": "None indicated. Routine surveillance every 6-12 months.",
        "Dosage": "N/A - Cerrahi odaklı takip."
    },
    "Grade 2": {
        "Diagnosis": "Intermediate-Grade Localized RCC",
        "Survival": "5-Year Overall Survival: ~80-85%",
        "Treatment": "Partial Nephrectomy preferred; Radical Nephrectomy if tumor is central or T2.",
        "Adjuvant": "Consider Adjuvant Pembrolizumab if high-risk features (pT2, Grade 4 or sarcomatoid) are present.",
        "Dosage": "Pembrolizumab: 200mg IV every 3 weeks or 400mg every 6 weeks for up to 1 year."
    },
    "Grade 3": {
        "Diagnosis": "High-Grade Regional RCC",
        "Survival": "5-Year Overall Survival: ~60-70% | Yüksek nüks riski.",
        "Treatment": "Radical Nephrectomy with lymph node dissection if nodes are clinically enlarged.",
        "Adjuvant": "Adjuvant Pembrolizumab is the standard of care for high-risk resected disease.",
        "Dosage": "Pembrolizumab: 200mg q3w. Klinik çalışmalar TKI (ör. Sunitinib) önerebilir ancak IO tercih edilir."
    },
    "Grade 4": {
        "Diagnosis": "Very High-Grade / Sarcomatoid RCC",
        "Survival": "5-Year Overall Survival: ~40-55% | Agresif neoplastik davranış.",
        "Treatment": "Aggressive Radical Nephrectomy. Erken sistemik tedavi için multidisipliner konsültasyon.",
        "Adjuvant": "Strong recommendation for Adjuvant Immunotherapy (Pembrolizumab).",
        "Dosage": "Pembrolizumab 200mg IV. Metastatik ilerleme açısından çok yakın takip gereklidir."
    },
    "Stage IV (M1)": {
        "Diagnosis": "Metastatic Renal Cell Carcinoma (Stage IV)",
        "Survival": "Median OS: ~55.7 ay (IO-IO) | Median PFS: ~23.9 ay (IO-TKI).",
        "Treatment": "Sistemik tedavi birincil seçenektir. Sitoredüktif nefrektomi seçili vakalarda düşünülür.",
        "Adjuvant": "N/A (Sistemik Odaklı)",
        "Dosage": "Seçenek A (IO-IO): Nivolumab 3mg/kg + Ipilimumab 1mg/kg q3w (4 doz).\nSeçenek B (IO-TKI): Lenvatinib 20mg PO günlük + Pembrolizumab 200mg IV q3w."
    }
}

# --- Advanced Vision Engine ---
def process_pathology_vision(image_rgb):
    # 1. Image Enhancement: Unsharp Mask
    gray = color.rgb2gray(image_rgb)
    sharpened = filters.unsharp_mask(gray, radius=1.5, amount=2.0)

    # 2. GLCM Feature Extraction
    u_img = util.img_as_ubyte(sharpened)
    glcm = feature.graycomatrix(u_img, [1, 3], [0, np.pi/4, np.pi/2, 3*np.pi/4], 256, symmetric=True, normed=True)
    contrast = feature.graycoprops(glcm, 'contrast').mean()
    homogeneity = feature.graycoprops(glcm, 'homogeneity').mean()

    # 3. Topological Risk Heatmap (Laplacian Variance)
    lap = filters.laplace(gray)
    heatmap = filters.gaussian(np.abs(lap), sigma=3)
    heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-8)

    # 4. Automated Grading Logic
    if contrast > 280 or homogeneity < 0.12: pred_grade = "Grade 4"
    elif contrast > 140: pred_grade = "Grade 3"
    elif contrast > 65: pred_grade = "Grade 2"
    else: pred_grade = "Grade 1"

    return sharpened, heatmap, pred_grade, contrast, homogeneity

# --- Streamlit Academic Dashboard UI ---
st.set_page_config(page_title="MathRIX AI v3.0", layout="wide")

st.title("⚕ MathRIX AI - Profesyonel Böbrek Kanseri Analiz Sistemi")
st.markdown("**Akademik Karar Destek Sistemi (2025-2026 NCCN/EAU Rehberleri Entegrasyonu)**")

# Sidebar
st.sidebar.header("Hasta Verileri")
pid = st.sidebar.text_input("Hasta Tanımlayıcı (ID)", "RCC-2026-X")
m1_override = st.sidebar.toggle("Metastaz (M1) Belirlendi (Global Override)")

upload = st.file_uploader("Patoloji Slaytı Yükle (H&E Görüntüsü)", type=['png', 'jpg', 'jpeg', 'tif'])

if upload:
    img_raw = Image.open(upload).convert("RGB")

    with st.spinner("Görüntü Netleştiriliyor ve Neoplastik Karmaşıklık Analiz Ediliyor..."):
        sharp, risk_map, grade, con, homo = process_pathology_vision(np.array(img_raw))

    # Logic: Link Grade to Protocols
    key = "Stage IV (M1)" if m1_override else grade
    data = CLINICAL_GUIDELINES[key]

    # Tabs for Organization
    tab1, tab2 = st.tabs(["Görüntüleme ve AI Analizi", "Klinik Protokol ve Tedavi Rehberi"])

    with tab1:
        st.header("Vizyon Motoru Çıktıları")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("AI Tahmini Derece (Grade)", grade)
        col_m2.metric("Doku Kontrastı (GLCM)", f"{con:.2f}")
        col_m3.metric("Topolojik Varyans", "Yüksek" if con > 200 else "Normal")

        v1, v2 = st.columns(2)
        v1.image(sharp, caption="Netleştirilmiş (Sharpened) Histoloji", use_container_width=True)
        v2.image(risk_map, caption="Topolojik Risk Haritası (Laplacian)", use_container_width=True, clamp=True)

    with tab2:
        st.header(f"Klinik Tanı ve Öneriler: {data['Diagnosis']}")
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Cerrahi ve Adjuvan Plan")
            st.write(f"**Cerrahi Öneri:** {data['Treatment']}")
            st.write(f"**Adjuvan Strateji:** {data['Adjuvant']}")
        with c2:
            st.subheader("Sistemik Veriler ve Sağkalım")
            st.write(f"**Sağkalım İstatistikleri:** {data['Survival']}")
            st.write(f"**İlaç Dozaj Şeması:** {data['Dosage']}")

    # Excel Report Generation
    report_df = pd.DataFrame({
        "Patient ID": [pid],
        "Metastasis Status": ["Positive" if m1_override else "Negative"],
        "AI Predicted Grade": [grade],
        "Diagnosis": [data['Diagnosis']],
        "Surgical Treatment": [data['Treatment']],
        "Drug Dosage": [data['Dosage']],
        "OS Statistics": [data['Survival']]
    })

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, index=False, sheet_name='MathRIX_Analysis')

    st.sidebar.download_button(
        label="↓ Klinik Raporu İndir (Excel)",
        data=buffer.getvalue(),
        file_name=f"MathRIX_AI_Rapor_{pid}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Analizi başlatmak için lütfen bir patoloji slaytı yükleyin.")
