import streamlit as st
import numpy as np
import pandas as pd
import io
from PIL import Image
from skimage import color, feature, filters, util

# --- ADVANCED CLINICAL INTELLIGENCE DATABASE (2025-2026 Context) ---
CLINICAL_DB_V4 = {
    "Grade 1": {
        "Status": "Localized / Low Risk",
        "Surgical": "Partial Nephrectomy (NSS) preferred for T1a (<=4cm).",
        "Adjuvant": "No adjuvant therapy indicated.",
        "Survival": "5-year OS: >95%",
        "Systemic": "N/A (Localized)"
    },
    "Grade 2": {
        "Status": "Localized / Intermediate Risk",
        "Surgical": "Partial Nephrectomy (NSS) preferred; Radical if complex anatomy.",
        "Adjuvant": "Pembrolizumab (200mg q3w) if pT2 and high-risk features present.",
        "Survival": "5-year OS: ~85%",
        "Systemic": "N/A (Localized)"
    },
    "Grade 3": {
        "Status": "Regional / High Risk",
        "Surgical": "Radical Nephrectomy + Lymph Node Dissection (if clinically indicated).",
        "Adjuvant": "Standard: Adjuvant Pembrolizumab for 1 year.",
        "Survival": "5-year OS: ~65%",
        "Systemic": "N/A (Localized)"
    },
    "Grade 4": {
        "Status": "Aggressive / Sarcomatoid Features",
        "Surgical": "Extensive Radical Nephrectomy; consider venous thrombectomy if pT3a vascular invasion found.",
        "Adjuvant": "Mandatory: Pembrolizumab consultation.",
        "Survival": "5-year OS: <50%",
        "Systemic": "Evaluate for early systemic involvement."
    },
    "Stage IV (M1) Override": {
        "Status": "Metastatic Disease (Global Override Active)",
        "Surgical": "Cytoreductive nephrectomy in selected patients only (IMDC risk stratified).",
        "Adjuvant": "N/A (Systemic focus)",
        "Systemic": "IO-IO: Nivolumab (3mg/kg) + Ipilimumab (1mg/kg) q3w x4 doses.\nIO-TKI: Lenvatinib (20mg daily) + Pembrolizumab (200mg q3w).",
        "Supportive": "Bone: Bisphosphonates (Zoledronic acid 4mg q4w) or Denosumab (120mg q4w). Brain: SRS criteria.",
        "Survival": "Median OS: ~55.7 months (Nivo+Ipi) | Median PFS: ~23.9 months (Lenv+Pembro)"
    }
}

# --- WEIGHTED TEXTURE SCORING ENGINE ---
def calculate_diagnostics(image_rgb):
    gray = color.rgb2gray(image_rgb)
    sharpened = filters.unsharp_mask(gray, radius=1.0, amount=1.5)
    u_img = util.img_as_ubyte(sharpened)

    # GLCM Metrics
    glcm = feature.graycomatrix(u_img, [1, 3], [0, np.pi/2], 256, symmetric=True, normed=True)
    metrics = {
        'contrast': feature.graycoprops(glcm, 'contrast').mean(),
        'dissimilarity': feature.graycoprops(glcm, 'dissimilarity').mean(),
        'homogeneity': feature.graycoprops(glcm, 'homogeneity').mean(),
        'correlation': feature.graycoprops(glcm, 'correlation').mean(),
        'energy': feature.graycoprops(glcm, 'energy').mean()
    }

    # Weighted Scoring Logic (Mathematical Classifier)
    metrics['weighted_score'] = (metrics['contrast'] * 0.4) + (metrics['dissimilarity'] * 0.3) - (metrics['homogeneity'] * 100 * 0.2) - (metrics['energy'] * 100 * 0.1)

    if metrics['weighted_score'] > 150: grade = "Grade 4"
    elif metrics['weighted_score'] > 80: grade = "Grade 3"
    elif metrics['weighted_score'] > 30: grade = "Grade 2"
    else: grade = "Grade 1"

    # Heatmap
    lap = filters.laplace(gray)
    heatmap = filters.gaussian(np.abs(lap), sigma=3)
    heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-8)

    return sharpened, heatmap, grade, metrics

# --- PROFESSIONAL STREAMLIT UI V4.0 ---
st.set_page_config(page_title="MathRIX AI v4.0", page_icon="⚕ ", layout="wide")
st.title("⚕ MathRIX AI v4.0 - Professional Academic Dashboard")
st.markdown("**Digital Pathology & Clinical Oncology Decision Support System (2025-2026 Guidelines)**")

# Sidebar Metadata
st.sidebar.header("Patient Metadata")
pid = st.sidebar.text_input("Patient Identifier", "RCC-2026-BETA")
m1_toggle = st.sidebar.toggle("Metastatic Involvement (M1)", value=False)
gtruth = st.sidebar.selectbox("Pathologist Verified Ground Truth (Grade)", ["Grade 1", "Grade 2", "Grade 3", "Grade 4"])

upload = st.file_uploader("Upload Histopathology Image (H&E)", type=['png', 'jpg', 'jpeg', 'tif'])

if upload:
    img_raw = Image.open(upload).convert("RGB")

    with st.spinner("Initializing Vision Engine & Weighted Classification..."):
        sharp, risk_map, ai_grade, m = calculate_diagnostics(np.array(img_raw))

    # Logic Mapping
    active_key = "Stage IV (M1)" if m1_toggle else ai_grade
    proto = CLINICAL_DB_V4[active_key]

    # Academic Layout: Tabs
    tab1, tab2 = st.tabs(["⌒ Vision Diagnostics & AI Analysis", "⌑ Clinical Protocols & Guidelines"])

    with tab1:
        if m1_toggle:
            st.error("☐ GLOBAL OVERRIDE STATUS: Metastatic Protocol (Stage IV) is currently prioritized.")

        # Metric Grid
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("AI Grade Prediction", ai_grade)
        col_m2.metric("Contrast", f"{m['contrast']:.2f}")
        col_m3.metric("Homogeneity", f"{m['homogeneity']:.4f}")
        col_m4.metric("Weighted Texture Score", f"{m['weighted_score']:.1f}")

        # Visual Expert Correlation
        v1, v2 = st.columns(2)
        v1.image(sharp, caption="Sharpened Histology Slide (Nuclear Detail Enhanced)", use_container_width=True)
        v2.image(risk_map, caption="Topological Risk Heatmap (Neoplastic Complexity)", use_container_width=True, clamp=True)

        # Validation & Discordance Section
        st.divider()
        st.subheader("Validation & Discordance Analysis")
        if ai_grade == gtruth:
            st.success(f"✅ AI Prediction matches Ground Truth ({gtruth}). Clinical confidence: High.")
        else:
            st.warning(f"☐ DISCORDANCE DETECTED: AI predicted {ai_grade} vs. Pathologist {gtruth}. Immediate review of morphological variance recommended.")

    with tab2:
        st.subheader(f"Targeted Management Strategy: {active_key}")
        st.write(f"**Current Diagnostic Status:** {proto.get('Status', 'N/A')}")
        st.divider()

        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown("#### Surgical & Adjuvant Scheme")
            st.write(f"**Surgical Plan:** {proto.get('Surgical', 'N/A')}")
            st.write(f"**Adjuvant Strategy:** {proto.get('Adjuvant', 'N/A')}")
        with sc2:
            st.markdown("#### Systemic & Survival Projections")
            if m1_toggle:
                st.write(f"**First-Line Seq:** {proto['FirstLine']}")
                st.write(f"**Second-Line Seq:** {proto['SecondLine']}")
                st.write(f"**Skeletal Support:** {proto['Supportive']}")
            else:
                st.write(f"**Systemic Action:** {proto.get('Systemic', 'N/A')}")
            st.write(f"**Survival Statistic:** {proto['Survival']}")

    # Excel Report Generation
    report_df = pd.DataFrame({
        "Patient ID": [pid],
        "Metastasis Override": ["ACTIVE" if m1_toggle else "INACTIVE"],
        "AI Grade Prediction": [ai_grade],
        "Pathologist Ground Truth": [gtruth],
        "Discordance Margin": ["0%" if ai_grade == gtruth else "Discordance"],
        "Weighted Score": [m['weighted_score']],
        "Survival Projection": [proto['Survival']],
        "Treatment Recommendation": [proto['Systemic'] if m1_toggle else proto['Surgical']]
    })

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, index=False, sheet_name='Institutional_Analysis')

    st.sidebar.download_button(
        label="⎇ Download Academic Report (Excel)",
        data=buffer.getvalue(),
        file_name=f"MathRIX_AI_V4_{pid}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Please upload a pathology slide to begin morphological analysis.")
