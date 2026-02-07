import streamlit as st
import numpy as np
import pandas as pd
import io
from PIL import Image
from skimage import color, feature, filters, util

# --- ADVANCED ACADEMIC CLINICAL DATABASE (v5.0) ---
CLINICAL_DB_V5 = {
    "Grade 1": {
        "Status": "Localized / Low Neoplastic Complexity",
        "Surgical_Procedures": "Partial Nephrectomy (PN) preferred for nephron preservation.",
        "Surgical_Complications": ["Intraoperative hemorrhage (<500cc)", "Postoperative urinary fistula (rare)", "Acute kidney injury (transient)"],
        "Adjuvant_Strategy": "None indicated; Active Surveillance protocol.",
        "Survival_Model": {"5-Year OS": ">95%", "Recurrence_Rate": "<5%"},
        "Systemic_Protocol": "N/A - Localized Focus"
    },
    "Grade 2": {
        "Status": "Localized / Intermediate Complexity",
        "Surgical_Procedures": "Partial Nephrectomy (NSS) vs. Radical Nephrectomy (RN) if central.",
        "Surgical_Complications": ["Lymphatic leak", "Wound infection (SSI)", "Pseudoaneurysm"],
        "Adjuvant_Strategy": "Pembrolizumab (200mg q3w) if pT2 + Grade 4/Sarcomatoid.",
        "Survival_Model": {"5-Year OS": "~85-90%", "Recurrence_Risk": "Moderate"},
        "Systemic_Protocol": "N/A - Localized Focus"
    },
    "Grade 3": {
        "Status": "Regional / High Neoplastic Complexity",
        "Surgical_Procedures": "Radical Nephrectomy + regional lymphadenectomy.",
        "Surgical_Complications": ["Deep Vein Thrombosis (DVT)", "Intestinal ileus", "Diaphragmatic injury"],
        "Adjuvant_Strategy": "Adjuvant Pembrolizumab (Keynote-564 protocol) strongly recommended.",
        "Survival_Model": {"5-Year OS": "~60-70%", "Recurrence_Rate": "20-35%"},
        "Systemic_Protocol": "N/A - Localized Focus"
    },
    "Grade 4": {
        "Status": "Aggressive / Sarcomatoid or Rhabdoid Features",
        "Surgical_Procedures": "Radical Nephrectomy + Caval Thrombectomy if pT3a vascular invasion.",
        "Surgical_Complications": ["Pulmonary embolism (PE)", "Major venous hemorrhage", "Multi-organ failure"],
        "Adjuvant_Strategy": "Mandatory clinical trial or Adjuvant Pembrolizumab consultation.",
        "Survival_Model": {"5-Year OS": "~40-50%", "Progression_Time": "Rapid (<12 months)"},
        "Systemic_Protocol": "Evaluate for early systemic involvement."
    },
    "Stage IV (M1)": {
        "Status": "Advanced Metastatic Disease",
        "Surgical_Procedures": "Cytoreductive nephrectomy in selected patients only (IMDC risk stratified).",
        "Surgical_Complications": ["Delayed wound healing due to TKIs", "Incisional hernia", "Metabolic imbalance"],
        "Systemic_Protocol": "1L: Nivolumab + Ipilimumab OR Lenvatinib + Pembrolizumab.",
        "irAE_Monitoring": {"Colitis": "Hold IO, start Steroids", "Hepatitis": "LFTs >3x ULN = Steroids"},
        "Survival_Model": {"Median OS": "~55.7 months", "PFS": "~23.9 months"}
    }
}

# --- VISION LOGIC RECALIBRATION CORE ---
def run_hybrid_vision(image_rgb):
    gray = color.rgb2gray(image_rgb)
    sharpened = filters.unsharp_mask(gray, radius=1.0, amount=1.5)
    u_img = util.img_as_ubyte(sharpened)

    glcm = feature.graycomatrix(u_img, [1, 3], [0, np.pi/4, np.pi/2, 3*np.pi/4], 256, symmetric=True, normed=True)
    contrast = feature.graycoprops(glcm, 'contrast').mean()
    asm = feature.graycoprops(glcm, 'ASM').mean()
    correlation = feature.graycoprops(glcm, 'correlation').mean()

    n_contrast = np.clip(contrast / 500, 0, 1)
    n_asm = np.clip(asm, 0, 1)
    n_correlation = np.clip((correlation + 1) / 2, 0, 1)

    score = ((n_contrast * 0.5) + ((1 - n_asm) * 0.3) + ((1 - n_correlation) * 0.2)) * 100

    if score > 75: grade = "Grade 4"
    elif score > 50: grade = "Grade 3"
    elif score > 25: grade = "Grade 2"
    else: grade = "Grade 1"

    lap = filters.laplace(gray)
    heatmap = filters.gaussian(np.abs(lap), sigma=3)
    heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-8)

    return grade, heatmap, {'Score': score, 'Contrast': contrast, 'ASM': asm, 'Correlation': correlation, 'N_Contrast': n_contrast, 'N_ASM': n_asm, 'N_Correlation': n_correlation}

# --- STREAMLIT UI v5.0 ---
st.set_page_config(page_title="MathRIX AI v5.0", page_icon="⚕", layout="wide")

# Sidebar - Institutional Branding & Metadata
st.sidebar.markdown("## ⚕ MathRIX AI v5.0\n*Institutional Clinical Dashboard*")
st.sidebar.divider()
with st.sidebar.form("patient_metadata"):
    st.subheader("Patient Metadata")
    pid = st.text_input("Patient ID", "RCC-2026-V5")
    m1_override = st.toggle("Metastatic Stage (M1)", value=False)
    st.form_submit_button("Update Context")

# Main Layout
st.title("Renal Cell Carcinoma (RCC) Academic Dashboard")
st.markdown("### Diagnostic & Protocol Centralization Engine")

upload = st.file_uploader("Upload Renal Histopathology Slide", type=['png', 'jpg', 'jpeg', 'tif'])

if upload:
    img_raw = Image.open(upload).convert("RGB")

    # Vision Logic Integration
    with st.spinner("Performing Hybrid GLCM Recalibration..."):
        grade, risk_map, m = run_hybrid_vision(np.array(img_raw))

    final_key = "Stage IV (M1)" if m1_override else grade
    db_node = CLINICAL_DB_V5[final_key]

    # Primary Diagnostics Tab
    t1, t2, t3 = st.tabs(["። Vision Diagnostics", "፡ Surgical Strategies", "፡ Systemic Protocols"])

    with t1:
        if m1_override: st.error("☐ GLOBAL OVERRIDE STATUS: Metastatic Protocol (Stage IV) is currently prioritized.")

        mc1, mc2 = st.columns(2)
        mc1.metric("Hybrid Texture Score", f"{m['Score']:.2f}")
        mc2.metric("AI Grade Assessment", grade)

        st.subheader("Topological Risk Assessment")
        zoom_lvl = st.slider("Visual Zoom Level", 300, 1000, 600)
        v1, v2 = st.columns(2)
        v1.image(img_raw, caption="Original Slide View", width=zoom_lvl)
        v2.image(risk_map, caption="Topological Risk Heatmap", width=zoom_lvl, clamp=True)

        with st.expander("Detailed Mathematical Texture Breakdown"):
            st.write(f"**GLCM Contrast:** {m['Contrast']:.2f} | **ASM (Chaos):** {m['ASM']:.4f} | **Correlation:** {m['Correlation']:.4f}")
            st.info("Scoring Logic: 50% Contrast + 30% Inverse ASM + 20% Inverse Correlation")

        st.divider()
        st.subheader("Pathologist Truth Comparison")
        truth = st.selectbox("Input Verified Ground Truth Grade", ["Grade 1", "Grade 2", "Grade 3", "Grade 4"])
        if grade == truth:
            st.success(f"**Validation Status: MATCH - AI and Pathologist in agreement ({truth})**")
        else:
            st.warning(f"**Validation Status: DISCORDANCE - AI: {grade} vs Pathologist: {truth}**")

    with t2:
        st.header(f"Surgical Management for {final_key}")
        st.write(f"**Status:** {db_node['Status']}")
        st.markdown(f"**Surgical Procedures:**\n{db_node['Surgical_Procedures']}")
        st.markdown("**Surgical Complication Risks:**")
        for comp in db_node['Surgical_Complications']: st.write(f"- {comp}")
        st.markdown(f"**Adjuvant Strategy:**\n{db_node['Adjuvant_Strategy']}")

    with t3:
        st.header(f"Systemic & Survival Profile")
        if "Systemic_Protocol" in db_node: st.markdown(f"**Systemic Protocol:**\n{db_node['Systemic_Protocol']}")
        if "irAE_Monitoring" in db_node:
            st.subheader("irAE Clinical Monitoring")
            st.json(db_node['irAE_Monitoring'])
        st.subheader("Advanced Survival Model")
        st.table(pd.DataFrame(db_node['Survival_Model'].items(), columns=['Metric', 'Value']))

    # Institutional Reporting Module (Excel)
    st.sidebar.divider()
    st.sidebar.subheader("Institutional Audit Reporting")

    # Page 1: Clinical Risk Analysis
    clinical_audit_data = {
        "Metric Category": [
            "Case Information", "Case Information", "AI Diagnostic Assessment", "Clinical Validation",
            "Surgical Risk Analysis", "Surgical Risk Analysis",
            "Oncology Protocol", "Oncology Protocol", "Survival Projections"
        ],
        "Data Point": [
            "Patient Identifier", "Metastatic Toggle", "AI Predicted Grade", "Pathologist Ground Truth",
            "Recommended Procedure", "Anticipated Complications",
            "Adjuvant/Systemic Strategy", "irAE Monitoring Protocol", "Survival Probability (5-Yr OS)"
        ],
        "Value": [
            pid, "Active (M1)" if m1_override else "Inactive (M0)", grade, truth,
            db_node.get('Surgical_Procedures', 'N/A'), ", ".join(db_node['Surgical_Complications']),
            db_node.get('Systemic_Protocol', db_node.get('Adjuvant_Strategy')),
            str(db_node.get('irAE_Monitoring', 'N/A')), str(db_node['Survival_Model'].get('5-Year OS', 'N/A'))
        ]
    }

    # Page 2: Mathematical Vision Proofs
    vision_proof_data = {
        "Vision Parameter": [
            "Scoring Formula", "Weighted Result", "Raw Contrast", "Raw ASM", "Raw Correlation",
            "Normalized Contrast (C/500)", "Normalized ASM", "Normalized Correlation ((Cor+1)/2)"
        ],
        "Value/Proof": [
            "(N_Contrast * 0.5) + ((1 - N_ASM) * 0.3) + ((1 - N_Correlation) * 0.2)",
            f"{m['Score']:.4f}", f"{m['Contrast']:.4f}", f"{m['ASM']:.6f}", f"{m['Correlation']:.4f}",
            f"{m['N_Contrast']:.4f}", f"{m['N_ASM']:.4f}", f"{m['N_Correlation']:.4f}"
        ]
    }

    df_clinical = pd.DataFrame(clinical_audit_data)
    df_vision = pd.DataFrame(vision_proof_data)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_clinical.to_excel(writer, index=False, sheet_name='Clinical_Risk_Analysis')
        df_vision.to_excel(writer, index=False, sheet_name='Vision_Mathematical_Proofs')
        
        # Auto-adjust column widths for readability
        for sheet in ['Clinical_Risk_Analysis', 'Vision_Mathematical_Proofs']:
            worksheet = writer.sheets[sheet]
            worksheet.set_column('A:C', 35)

    st.sidebar.download_button(
        label="⎇ Export Audit Report (Excel)",
        data=buffer.getvalue(),
        file_name=f"MathRIX_Audit_V5_{pid}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Please upload a slide to initiate diagnostic analysis.")
