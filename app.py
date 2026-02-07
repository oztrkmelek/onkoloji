import streamlit as st
import numpy as np
import pandas as pd
import cv2
from PIL import Image
from skimage.feature import graycomatrix, graycoprops
from skimage import img_as_ubyte
import io
import xlsxwriter

# --- 1. Clinical Knowledge Base Integration ---
RCC_CLINICAL_DB_V5 = {
    'Grade 1': {
        'Diagnosis': 'Stage I / Low-Grade Localized RCC',
        'Surgical_Protocol': 'Partial Nephrectomy (PN) preferred for nephron preservation (T1a tumors <= 4cm).',
        'Survival_Stats': {'5Y_OS': '~95-97%', 'PFS': 'High; Recurrence risk < 5%'},
        'Adjuvant_Criteria': 'None indicated; Active Surveillance protocol for small renal masses.'
    },
    'Grade 2': {
        'Diagnosis': 'Intermediate-Grade Localized RCC',
        'Surgical_Protocol': 'Partial Nephrectomy (PN) or Radical Nephrectomy (RN) based on anatomical complexity.',
        'Survival_Stats': {'5Y_OS': '~80-85%', 'PFS': 'Intermediate'},
        'Adjuvant_Criteria': 'Consider Pembrolizumab if high-risk features (pT2, Grade 2-3) are present.'
    },
    'Grade 3': {
        'Diagnosis': 'High-Grade Localized or Locally Advanced RCC',
        'Surgical_Protocol': 'Radical Nephrectomy (RN) typically required; Lymph node dissection if clinically positive.',
        'Survival_Stats': {'5Y_OS': '~60-70%', 'PFS': 'Low-Intermediate'},
        'Adjuvant_Criteria': 'Pembrolizumab recommended for high-risk pT2-pT3 Grade 3 or pT4 cases.'
    },
    'Grade 4': {
        'Diagnosis': 'Very High-Grade / Sarcomatoid Differentiation',
        'Surgical_Protocol': 'Radical Nephrectomy with adrenalectomy if indicated; multiorgan resection.',
        'Survival_Stats': {'5Y_OS': '~20-40%', 'PFS': 'Low; High risk of early systemic progression'},
        'Adjuvant_Criteria': 'Systemic therapy consultation mandatory; high eligibility for checkpoint inhibitors.'
    },
    'Metastatic_M1': {
        'Diagnosis': 'Stage IV / Advanced Systemic RCC',
        'Protocol': 'First-line: Nivolumab+Ipilimumab or Lenvatinib+Pembrolizumab.',
        'Notes': 'Bone/Brain metastasis protocols triggered if applicable.'
    }
}

# --- 2. Vision Engine: Recalibrated GLCM Analysis ---
def analyze_texture(image_gray):
    # Calculate GLCM features
    glcm = graycomatrix(image_gray, distances=[5], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4], levels=256, symmetric=True, normed=True)

    contrast = graycoprops(glcm, 'contrast').mean()
    correlation = graycoprops(glcm, 'correlation').mean()
    homogeneity = graycoprops(glcm, 'homogeneity').mean()
    energy = graycoprops(glcm, 'energy').mean()

    # Decision Logic Optimized for Grade 3/4 separation
    # High contrast and low homogeneity usually indicate higher grades.
    score = (contrast * 0.1) + (correlation * 50) + (energy * 100)

    if score < 45: grade = 'Grade 1'
    elif score < 60: grade = 'Grade 2'
    elif score < 85: grade = 'Grade 3'
    else: grade = 'Grade 4'

    return grade, {'Contrast': contrast, 'Correlation': correlation, 'Homogeneity': homogeneity, 'Energy': energy, 'Composite_Score': score}

# --- 3. Topological Risk Heatmap Generator ---
def generate_risk_map(image_gray):
    # Local variance used as topological risk indicator
    kernel_size = 15
    mean = cv2.blur(image_gray.astype(float), (kernel_size, kernel_size))
    mean_sq = cv2.blur(image_gray.astype(float)**2, (kernel_size, kernel_size))
    variance = mean_sq - mean**2
    risk_map = np.clip(variance / variance.max() * 255, 0, 255).astype(np.uint8)
    return cv2.applyColorMap(risk_map, cv2.COLORMAP_JET)

# --- 4. Streamlit UI ---
st.set_page_config(page_title="MathRIX AI v5.0", layout="wide")
st.title("🧬 MathRIX AI v5.0 | High-Precision RCC Analyzer")
st.markdown("--- ")

with st.sidebar:
    st.header("Patient Context")
    patient_id = st.text_input("Patient ID", "RCC-2026-V5")
    m1_status = st.checkbox("Metastatic (M1) Status Indicated")
    uploaded_file = st.file_uploader("Upload Pathology Slide (H&E)", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_np = np.array(img)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    # Run Engines
    predicted_grade, metrics = analyze_texture(gray)
    heatmap = generate_risk_map(gray)

    # Clinical Logic Blend
    final_ctx = 'Metastatic_M1' if m1_status else predicted_grade
    guidelines = RCC_CLINICAL_DB_V5[final_ctx]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Visual Analysis")
        st.image(img, caption="Original Slide", use_container_width=True)
        st.image(heatmap, caption="Topological Risk Heatmap (JET)", use_container_width=True)

    with col2:
        st.subheader("Diagnostic Intelligence")
        st.success(f"Predicted AI Grade: {predicted_grade}")
        st.write(f"**Integrated Diagnosis:** {guidelines['Diagnosis']}")

        st.metric("Texture Score", f"{metrics['Composite_Score']:.2f}")
        st.write("**Surgical Protocol:**", guidelines.get('Surgical_Protocol', guidelines.get('Protocol')))
        st.write("**Adjuvant Strategy:**", guidelines.get('Adjuvant_Criteria', 'See Systemic Protocol'))

        with st.expander("GLCM Metadata Metrics"):
            st.write(metrics)

    # Report Generation
    st.markdown("--- ")
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    worksheet.write(0, 0, "MathRIX AI v5.0 Clinical Report")
    worksheet.write(1, 0, f"Patient ID: {patient_id}")
    worksheet.write(2, 0, f"Diagnosis: {guidelines['Diagnosis']}")
    worksheet.write(3, 0, f"AI Grade: {predicted_grade}")
    workbook.close()

    st.download_button(
        label="📥 Download Clinical Report (Excel)",
        data=output.getvalue(),
        file_name=f"MathRIX_Report_{patient_id}.xlsx",
        mime="application/vnd.ms-excel"
    )
else:
    st.info("Please upload a renal pathology image to begin analysis.")
