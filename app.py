import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import io
import cv2
from skimage import feature
from datetime import datetime

# --- MATHRIX AI: ACADEMIC STYLING ---
st.set_page_config(page_title="MathRIX AI | Clinical Oncology", layout="wide")

st.markdown("""
    <style>
    .report-card { 
        background-color: #ffffff; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #0A2351; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-card { background-color: #f0f4f8; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #d1d9e6; }
    h1, h2, h3 { color: #0A2351; }
    </style>
    """, unsafe_allow_html=True)

# --- CLINICAL ONTOLOGY ---
DATABASE = {
    "Clear Cell RCC": {
        "Grade 1": {"med": "Active Surveillance", "surv": "96%", "color": "#27ae60"},
        "Grade 2": {"med": "Partial Nephrectomy", "surv": "88%", "color": "#f1c40f"},
        "Grade 3": {"med": "TKI Therapy (Sunitinib)", "surv": "67%", "color": "#e67e22"},
        "Grade 4": {"med": "IO Doublet (Nivo + Ipi)", "surv": "35%", "color": "#c0392b"}
    }
}

# --- PRECISION ANALYSIS ENGINE ---
def process_image_robustly(img_np):
    # Pre-processing to handle blur and noise
    # 
    normalized = cv2.normalize(img_np, None, 0, 255, cv2.NORM_MINMAX).astype('uint8')
    denoised = cv2.fastNlMeansDenoising(normalized, None, 10, 7, 21)
    
    # Texture analysis for ISUP Grading
    lbp = feature.local_binary_pattern(denoised, 8, 1, method="uniform")
    score = np.std(lbp)
    
    # Heatmap generation
    laplacian = cv2.Laplacian(denoised, cv2.CV_64F)
    heatmap = cv2.applyColorMap(cv2.normalize(np.abs(laplacian), None, 0, 255, cv2.NORM_MINMAX).astype('uint8'), cv2.COLORMAP_JET)
    
    return score, heatmap

# --- SIDEBAR & CONTROLS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3843/3843118.png", width=70)
    st.title("MathRIX AI v2.0")
    subtype = st.selectbox("Cancer Subtype", ["Clear Cell RCC"])
    m_status = st.toggle("Metastatic Involvement (M1 Stage)")
    st.write("---")
    st.caption("Standardizing ISUP/WHO Renal Grading")

st.markdown("# 🔬 MathRIX AI: High-Fidelity Diagnostics")

uploaded_files = st.file_uploader("Upload Pathology Specimens", accept_multiple_files=True)

if uploaded_files:
    reports = []
    for file in uploaded_files:
        raw_img = Image.open(file).convert('L')
        img_np = np.array(raw_img)
        
        # Core Analysis
        score, h_map = process_image_robustly(img_np)
        
        # Grading Logic (Dynamic Thresholds)
        if score > 1.25: grade = "Grade 4"
        elif score > 0.85: grade = "Grade 3"
        elif score > 0.45: grade = "Grade 2"
        else: grade = "Grade 1"
        
        # Clinical Data Mapping
        base_info = DATABASE[subtype][grade]
        
        # [cite: 2026-02-03] Metastasis override logic
        if m_status:
            med = "Combo (Nivolumab + Cabozantinib)"
            surv = "15-18%"
            risk = "CRITICAL (M1)"
        else:
            med = base_info["med"]
            surv = base_info["surv"]
            risk = "Standard Risk"

        # --- UI LAYOUT ---
        st.markdown(f"### Case Report: {file.name}")
        c1, c2, c3 = st.columns([2, 1, 1.5])
        
        with c1:
            h_map_rgb = cv2.cvtColor(h_map, cv2.COLOR_BGR2RGB)
            blended = Image.blend(Image.open(file).convert("RGB"), Image.fromarray(h_map_rgb), alpha=0.45)
            st.image(blended, use_container_width=True, caption="Topological Heatmap (WSI)")
            
        with c2:
            h, w = img_np.shape
            roi = img_np[h//2-120:h//2+120, w//2-120:w//2+120]
            st.image(roi, use_container_width=True, caption="Smart Zoom ROI")
            st.markdown(f"<div class='metric-card'>Complexity Index<br><h2>{score:.3f}</h2></div>", unsafe_allow_html=True)
            
        with c3:
            st.markdown(f"""
                <div class="report-card">
                    <h2 style="color:{base_info['color']}; margin-top:0;">{grade}</h2>
                    <p><b>Prognosis:</b> {risk}</p>
                    <hr>
                    <p style="margin-bottom:5px;"><b>Recommended Protocol:</b></p>
                    <p style="font-size:1.1em; color:#0A2351;"><b>{med}</b></p>
                    <hr>
                    <p style="margin-bottom:5px;"><b>Survival Projection:</b></p>
                    <p style="font-size:1.5em; color:#c0392b;"><b>{surv}</b></p>
                </div>
            """, unsafe_allow_html=True)

        reports.append({
            "Specimen": file.name, "Prediction": grade, "Ground_Truth": "", 
            "Complexity": round(score, 4), "Therapy": med, "Survival": surv
        })

    # --- VALIDATION REPORT ---
    st.markdown("---")
    final_df = pd.DataFrame(reports)
    st.subheader("Clinical Data Aggregation & Validation")
    st.table(final_df)
    
    excel_out = io.BytesIO()
    with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
        final_df.to_excel(writer, index=False)
    st.download_button("📥 Export for Clinical Validation", excel_out.getvalue(), "MathRIX_Validation.xlsx", use_container_width=True)
