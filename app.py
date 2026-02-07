import streamlit as st
import numpy as np
import pandas as pd
import io
from PIL import Image
from skimage import color, feature, filters, util

# --- MathRIX AI: Finalized Clinical Decision Support App ---

# 1. 2025-2026 Clinical Protocol Mapping (NCCN/EAU)
CLINICAL_PROTOCOLS = {
    "Grade 1": "Active Surveillance or Partial Nephrectomy",
    "Grade 2": "Nephrectomy + Adjuvant Pembrolizumab (if high risk features present)",
    "Grade 3": "Nephrectomy + Adjuvant Pembrolizumab per EAU 2025 Protocols",
    "Grade 4": "Radical Nephrectomy + Systemic Adjuvant Therapy Consultation",
    "Stage IV (M1) Override": "First-line: Nivolumab + Ipilimumab OR Lenvatinib + Pembrolizumab"
}

# 2. Vision Analysis Layer Functions
def extract_vision_features(image_gray):
    """Layer 1: GLCM Texture Analysis"""
    image_uint = util.img_as_ubyte(image_gray)
    distances, angles = [1, 3], [0, np.pi/2]
    glcm = feature.graycomatrix(image_uint, distances=distances, angles=angles, levels=256, symmetric=True, normed=True)
    return {
        'contrast': feature.graycoprops(glcm, 'contrast').mean(),
        'homogeneity': feature.graycoprops(glcm, 'homogeneity').mean(),
        'correlation': feature.graycoprops(glcm, 'correlation').mean()
    }

def generate_risk_heatmap(image_gray):
    """Layer 2: Topological Heatmap using Laplacian Variance"""
    laplacian = filters.laplace(image_gray)
    heatmap = filters.gaussian(np.abs(laplacian), sigma=3)
    # Normalize for display
    return (heatmap - np.min(heatmap)) / (np.max(heatmap) - np.min(heatmap) + 1e-8)

# 3. Streamlit Interface Construction
st.set_page_config(page_title="MathRIX AI", page_icon="⚕ ", layout="wide")
st.title("MathRIX AI - Digital Pathology & Clinical Oncology Analyzer")
st.sidebar.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304731333a6d36a.svg", width=50)
st.sidebar.header("Patient Diagnostics")

patient_id = st.sidebar.text_input("Patient Identifier", value="RCC-2025-001")
metastasis_toggle = st.sidebar.toggle("Metastasis (M1) Detected", value=False)
ground_truth = st.sidebar.selectbox("Pathologist Verified Grade", ["Grade 1", "Grade 2", "Grade 3", "Grade 4"])

uploaded_file = st.file_uploader("Upload Renal Pathology Slide (H&E Image)", type=["jpg", "png", "tif"])

if uploaded_file:
    # Load and process image
    input_img = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(input_img)
    img_gray = color.rgb2gray(img_array)

    # Execute Vision Processing
    with st.spinner("Analyzing morphology and texture..."):
        features = extract_vision_features(img_gray)
        risk_map = generate_risk_heatmap(img_gray)

    # Automated Grade Prediction Logic (Heuristic based on GLCM contrast)
    if features['contrast'] > 250: predicted_grade = "Grade 4"
    elif features['contrast'] > 120: predicted_grade = "Grade 3"
    elif features['contrast'] > 40: predicted_grade = "Grade 2"
    else: predicted_grade = "Grade 1"

    # Link to Medication with Global Override for Metastasis
    if metastasis_toggle:
        final_recommendation = CLINICAL_PROTOCOLS["Stage IV (M1) Override"]
        diagnosis_label = "Advanced Metastatic RCC (Stage IV)"
    else:
        final_recommendation = CLINICAL_PROTOCOLS.get(predicted_grade)
        diagnosis_label = f"Localized Renal Cell Carcinoma ({predicted_grade})"

    # Layout Columns
    col1, col2 = st.columns(2)
    with col1:
        st.image(input_img, caption="Original Histopathology", use_container_width=True)
    with col2:
        st.image(risk_map, caption="Topological Risk Heatmap", use_container_width=True, clamp=True)

    # Results Display
    st.divider()
    st.subheader("Diagnostic Analysis & Clinical Linking")
    
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric(label="Texture Contrast (GLCM)", value=f"{features['contrast']:.2f}")
        st.info(f"**AI Predicted Grade:** {predicted_grade}")
    
    with res_col2:
        st.metric(label="Metastasis Override Status", value="ACTIVE" if metastasis_toggle else "INACTIVE")
        st.success(f"**Clinical Protocol:** {final_recommendation}")

    # Excel Report Export
    report_df = pd.DataFrame({
        "Patient ID": [patient_id],
        "AI Prediction": [predicted_grade],
        "Metastasis Override": ["YES" if metastasis_toggle else "NO"],
        "Latest Clinical Protocol": [final_recommendation],
        "Ground Truth (Verified)": [ground_truth],
        "Texture Contrast Score": [features['contrast']]
    })

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, index=False, sheet_name='MathRIX_Analysis')

    st.download_button(
        label="Download Clinical Report (Excel)",
        data=excel_buffer.getvalue(),
        file_name=f"MathRIX_AI_Report_{patient_id}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("Please upload a pathology slide to begin analysis.")
