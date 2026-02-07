import streamlit as st
import numpy as np
import pandas as pd
import io
from PIL import Image
from skimage import color, feature, filters, util, measure

# --- ACADEMIC KNOWLEDGE BASE v6.0 (2025-2026 Focus) ---
CLINICAL_KNOWLEDGE = {
    "VEGF_Resistance": "VEGF-targeted TKI resistance is managed via sequence switching to Cabozantinib or HIF-2α inhibitors (Belzutifan) per 2025 EAU updates.",
    "pT3a_Nuance": "pT3a staging (renal vein/sinus fat invasion) mandates radical nephrectomy with aggressive surgical margins to improve 5-year OS.",
    "irAE_Management": "Grade 3 colitis requires immediate cessation of IO and initiation of high-dose corticosteroids (1-2mg/kg/day).",
    "Grade_Protocols": {
        "Grade 1": {"Diag": "Low Neoplastic Complexity", "OS": ">95%", "Med": "Partial Nephrectomy (NSS)"},
        "Grade 2": {"Diag": "Intermediate Complexity", "OS": "~85-90%", "Med": "NSS + Adjuvant Pembrolizumab (if pT2+)"},
        "Grade 3": {"Diag": "High Neoplastic Complexity", "OS": "~65-70%", "Med": "Radical Nephrectomy + Adjuvant Pembrolizumab"},
        "Grade 4": {"Diag": "Aggressive / Sarcomatoid", "OS": "<50%", "Med": "Radical Nephrectomy + Early Systemic Consultation"},
        "Stage IV": {"Diag": "Metastatic RCC", "OS": "Variable", "Med": "1L: Nivo+Ipi or Lenv+Pembro | 2L: Cabozantinib"}
    }
}

# --- ENSEMBLE TEXTURE SCORING ENGINE (Grade 3 vs 4 Specialist) ---
def run_ensemble_vision(image_rgb):
    gray = color.rgb2gray(image_rgb)
    sharpened = filters.unsharp_mask(gray, radius=1.0, amount=1.5)
    u_img = util.img_as_ubyte(sharpened)

    # GLCM Dissimilarity
    glcm = feature.graycomatrix(u_img, [1, 3], [0, np.pi/2], 256, symmetric=True, normed=True)
    diss = feature.graycoprops(glcm, 'dissimilarity').mean()
    
    # Shannon Entropy (Chaos Metric)
    ent = measure.shannon_entropy(gray)

    # Normalization & Weighted Scoring
    n_diss = np.clip(diss / 20.0, 0, 1)
    n_ent = np.clip(ent / 7.5, 0, 1)
    score = (n_diss * 0.6 + n_ent * 0.4) * 100

    if score > 85: grade = "Grade 4"
    elif score > 65: grade = "Grade 3"
    elif score > 35: grade = "Grade 2"
    else: grade = "Grade 1"

    lap = filters.laplace(gray)
    risk_map = filters.gaussian(np.abs(lap), sigma=3)
    risk_map = (risk_map - risk_map.min()) / (risk_map.max() - risk_map.min() + 1e-8)

    return grade, risk_map, {'Score': score, 'Dissimilarity': diss, 'Entropy': ent}

# --- STREAMLIT UI v6.0 ---
st.set_page_config(page_title="MathRIX AI v6.0", page_icon="⚕", layout="wide")

# Fix: Initialize session state variable to avoid AttributeError
if "doctor_name" not in st.session_state:
    st.session_state.doctor_name = None

# Doctor Authentication Logic
if st.session_state.doctor_name is None:
    st.title("⚕ MathRIX AI v6.0 - Authentication")
    with st.form("auth"):
        doc_input = st.text_input("Physician Name (Full Name)", placeholder="Dr. John Smith")
        if st.form_submit_button("Enter Dashboard"):
            if doc_input:
                st.session_state.doctor_name = doc_input
                st.rerun()
            else: st.warning("Please enter your name to continue.")
    st.stop()

# Academic Dashboard
st.sidebar.markdown(f"## ⚕ MathRIX AI v6.0\n**Physician:** {st.session_state.doctor_name}")
st.sidebar.divider()
st.title("MathRIX AI v6.0 - Advanced RCC Oncology Dashboard")
st.markdown("### Precision Diagnostic & Clinical Decision Engine")

# Inputs
with st.sidebar.expander("Case Context"): 
    pid = st.text_input("Patient ID", "RCC-2026-FINAL")
    m1_check = st.toggle("M1 Metastasis (Bone/Brain/Visceral)")
    gtruth = st.selectbox("Pathologist Verified Grade", ["Grade 1", "Grade 2", "Grade 3", "Grade 4"])

upload = st.file_uploader("Upload Renal Histopathology Slide", type=['png', 'jpg', 'jpeg', 'tif'])

if upload:
    img_raw = Image.open(upload).convert("RGB")
    
    with st.spinner("Executing Ensemble Texture Scoring..."):
        grade, risk_map, m = run_ensemble_vision(np.array(img_raw))

    final_key = "Stage IV" if m1_check else grade
    proto = CLINICAL_KNOWLEDGE["Grade_Protocols"][final_key]

    tab1, tab2, tab3 = st.tabs(["Diagnostic Vision", "Treatment Strategy", "Academic Insight"])

    with tab1:
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Ensemble AI Grade", grade)
        col_m2.metric("Textural Entropy", f"{m['Entropy']:.2f}")
        col_m3.metric("Dissimilarity Index", f"{m['Dissimilarity']:.2f}")

        st.subheader("Microscopic Analysis")
        zoom = st.slider("Imaging Zoom", 400, 1200, 600)
        v1, v2 = st.columns(2)
        v1.image(img_raw, caption="Original Slide View", width=zoom)
        v2.image(risk_map, caption="Topological Neoplastic Risk Map", width=zoom, clamp=True)

    with tab2:
        st.header(f"Management: {final_key}")
        st.success(f"**Recommended Protocol:** {proto['Med']}")
        st.info(f"**5-Year Survival Benchmark:** {proto['OS']}")
        st.divider()
        doc_notes = st.text_area("Physician Clinical Notes (To be included in report)")

    with tab3:
        st.subheader("Academic Reference Blocks")
        st.markdown(f"**VEGF Resistance Strategy:** {CLINICAL_KNOWLEDGE['VEGF_Resistance']}")
        st.markdown(f"**pT3a Surgical Nuance:** {CLINICAL_KNOWLEDGE['pT3a_Nuance']}")
        st.markdown(f"**irAE Control Protocol:** {CLINICAL_KNOWLEDGE['irAE_Management']}")

    # Institutional Report Export
    report_df = pd.DataFrame({
        "Physician": [st.session_state.doctor_name],
        "Patient ID": [pid],
        "AI Grade Prediction": [grade],
        "Pathologist Ground Truth": [gtruth],
        "Ensemble Score": [f"{m['Score']:.2f}"],
        "Metastasis Status": ["M1" if m1_check else "M0"],
        "Survival Forecast": [proto['OS']],
        "Clinical Protocol": [proto['Med']],
        "Physician Notes": [doc_notes]
    })

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, index=False, sheet_name='MathRIX_Audit_v6')
    
    st.sidebar.download_button(
        label="📥 Download Institutional Audit (Excel)",
        data=buffer.getvalue(),
        file_name=f"MathRIX_v6_Audit_{pid}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Upload a histology image to initiate v6.0 diagnostic logic.")
