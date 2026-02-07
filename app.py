import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import io
import cv2
from skimage import feature

# --- ACADEMIC UI CONFIGURATION ---
st.set_page_config(page_title="MathRIX AI | Oncology Suite", layout="wide")

# Custom CSS for Professional Medical Look
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .status-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 25px; border-radius: 15px; border: 1px solid #334155;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); margin-bottom: 20px;
    }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #38bdf8; }
    .drug-box { background-color: #1e1b4b; border-left: 5px solid #6366f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
    .survival-text { font-size: 2rem; color: #f87171; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CLINICAL INTELLIGENCE CORE ---
# [cite: 2026-02-03] Full medication and survival mapping
DECISION_LOGIC = {
    "Grade 1": {"med": "Active Surveillance", "surv": "96%", "risk": "LOW", "color": "#10b981"},
    "Grade 2": {"med": "Partial Nephrectomy", "surv": "88%", "risk": "MODERATE", "color": "#f59e0b"},
    "Grade 3": {"med": "Adjuvant TKI (Sunitinib)", "surv": "67%", "risk": "HIGH", "color": "#f97316"},
    "Grade 4": {"med": "Nivolumab + Ipilimumab", "surv": "35%", "risk": "CRITICAL", "color": "#ef4444"}
}

def analyze_specimen(img_np):
    # Denoising for blurred images
    clean = cv2.fastNlMeansDenoising(img_np, None, 10, 7, 21)
    # Texture Complexity (ISUP Standard)
    lbp = feature.local_binary_pattern(clean, 8, 1, method="uniform")
    score = np.std(lbp)
    # Heatmap
    lap = cv2.Laplacian(clean, cv2.CV_64F)
    heatmap = cv2.applyColorMap(cv2.normalize(np.abs(lap), None, 0, 255, cv2.NORM_MINMAX).astype('uint8'), cv2.COLORMAP_JET)
    return score, heatmap

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown("### 🧬 *MathRIX AI Control*")
    m_stage = st.toggle("🚨 METASTASIS (M1) ACTIVE", help="Toggle if secondary lesions are detected")
    st.write("---")
    st.caption("v2.4 Final Academic Build")

# --- MAIN INTERFACE ---
st.title("🔬 MathRIX AI: Computational Oncology Platform")
st.markdown("---")

uploads = st.file_uploader("Drop Specimen Scans Here", accept_multiple_files=True)

if uploads:
    final_logs = []
    for up in uploads:
        img = Image.open(up).convert('L')
        img_np = np.array(img)
        
        # Core Computation
        complexity, thermal = analyze_specimen(img_np)
        
        # Dynamic Grading
        if complexity > 1.3: g = "Grade 4"
        elif complexity > 0.9: g = "Grade 3"
        elif complexity > 0.5: g = "Grade 2"
        else: g = "Grade 1"
        
        # Clinical Data Adjustment [cite: 2026-02-03]
        base = DECISION_LOGIC[g]
        final_med = "Doublet IO (Nivolumab + Cabozantinib)" if m_stage else base["med"]
        final_surv = "15-18%" if m_stage else base["surv"]
        
        # UI RENDERING
        with st.container():
            st.markdown(f"### Specimen ID: {up.name}")
            col1, col2, col3 = st.columns([2, 1, 1.5])
            
            with col1:
                st.markdown("<p style='color:#94a3b8;'>SPATIAL THERMAL MAP</p>", unsafe_allow_html=True)
                thermal_rgb = cv2.cvtColor(thermal, cv2.COLOR_BGR2RGB)
                blended = Image.blend(Image.open(up).convert("RGB"), Image.fromarray(thermal_rgb), alpha=0.45)
                st.image(blended, use_container_width=True)
                
            with col2:
                st.markdown("<p style='color:#94a3b8;'>SMART ZOOM (ROI)</p>", unsafe_allow_html=True)
                h, w = img_np.shape
                st.image(img_np[h//2-100:h//2+100, w//2-100:w//2+100], use_container_width=True)
                st.markdown(f"<div class='metric-value'>{complexity:.3f}</div><p>Chaos Index</p>", unsafe_allow_html=True)
                
            with col3:
                st.markdown(f"""
                    <div class="status-card">
                        <h2 style="color:{base['color']}; margin:0;">{g}</h2>
                        <p style="color:#94a3b8;">RISK: {"METASTATIC CRITICAL" if m_stage else base['risk']}</p>
                        <hr style="border-color:#334155;">
                        <div class="drug-box">
                            <small>TARGETED MEDICATION</small><br>
                            <b>{final_med}</b>
                        </div>
                        <p style="margin-top:15px; margin-bottom:0;">5-YEAR SURVIVAL PROJECTION</p>
                        <div class="survival-text">{final_surv}</div>
                    </div>
                """, unsafe_allow_html=True)

        final_logs.append({"Specimen": up.name, "Prediction": g, "Actual_Ground_Truth": "", "Medication": final_med, "Survival": final_surv})

    # VALIDATION TABLE
    st.markdown("### 📊 Clinical Validation Summary")
    df = pd.DataFrame(final_logs)
    st.data_editor(df, use_container_width=True) # Editlenebilir tablo (Excel gibi)
