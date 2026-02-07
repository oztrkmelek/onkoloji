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

# CSS ile kutucukları ve arayüzü güzelleştirelim
st.markdown("""
    <style>
    .report-card { 
        background-color: #ffffff; padding: 20px; border-radius: 15px; 
        border-left: 8px solid #0A2351; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .metric-box { background-color: #e3f2fd; padding: 10px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- CLINICAL DATABASE ---
ONCOLOGY_MAP = {
    "Clear Cell RCC": {
        "Grade 1": {"med": "Active Surveillance", "surv": "96%", "risk": "Low"},
        "Grade 2": {"med": "Partial Nephrectomy", "surv": "88%", "risk": "Moderate"},
        "Grade 3": {"med": "TKI Therapy (Sunitinib)", "surv": "67%", "risk": "High"},
        "Grade 4": {"med": "Nivolumab + Ipilimumab", "surv": "35%", "risk": "Critical"}
    }
}

# --- ANALİZ FONKSİYONLARI ---
def get_thermal_map(img_np):
    gray = cv2.normalize(img_np, None, 0, 255, cv2.NORM_MINMAX).astype('uint8')
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    norm_lap = cv2.normalize(np.abs(laplacian), None, 0, 255, cv2.NORM_MINMAX).astype('uint8')
    return cv2.applyColorMap(norm_lap, cv2.COLORMAP_JET)

def get_dynamic_score(crop):
    # Dokudaki gerçek karmaşayı (LBP) ölçer
    lbp = feature.local_binary_pattern(crop, 8, 1, method="uniform")
    return np.std(lbp)

# --- SIDEBAR ---
with st.sidebar:
    st.title("MathRIX AI")
    subtype = st.selectbox("Specimen Subtype", ["Clear Cell RCC"])
    m_stage = st.toggle("Metastatic Status (M1 Stage)") # BU BUTON ARTIK ÇALIŞIYOR
    st.write("---")
    st.info("Clinical Decision Support System")

st.markdown("# 🔬 MathRIX AI: Integrated Clinical Intelligence")

uploaded_files = st.file_uploader("Upload Digital Pathology Slides", accept_multiple_files=True)

if uploaded_files:
    summary_data = []
    for uploaded_file in uploaded_files:
        img = Image.open(uploaded_file).convert('L')
        img_np = np.array(img)
        
        # Isı haritası ve ROI
        t_map = get_thermal_map(img_np)
        h, w = img_np.shape
        roi = img_np[h//2-100:h//2+100, w//2-100:w//2+100]
        
        # SKORLAMA (Her resimde farklı sonuç vermesi için eşikleri hassaslaştırdık)
        score = get_dynamic_score(roi)
        if score > 1.3: grade = "Grade 4"
        elif score > 0.9: grade = "Grade 3"
        elif score > 0.6: grade = "Grade 2"
        else: grade = "Grade 1"
        
        # VERİ ÇEKME VE METASTAZ KONTROLÜ
        base = ONCOLOGY_MAP[subtype][grade]
        
        # Metastaz kontrolü (Eğer buton açıksa değerleri ez)
        if m_stage:
            display_med = "IO Combo (Nivolumab + Cabozantinib)"
            display_surv = "15-18%"
            risk_level = "CRITICAL (Stage IV)"
        else:
            display_med = base["med"]
            display_surv = base["surv"]
            risk_level = base["risk"]

        # --- GÖRSEL ARAYÜZ ---
        st.markdown(f"### Specimen: {uploaded_file.name}")
        c1, c2, c3 = st.columns([2, 1, 1.5])
        
        with c1:
            t_map_rgb = cv2.cvtColor(t_map, cv2.COLOR_BGR2RGB)
            blend = Image.blend(Image.open(uploaded_file).convert("RGB"), Image.fromarray(t_map_rgb), alpha=0.4)
            st.image(blend, use_container_width=True, caption="Thermal Hotspots")
            
        with c2:
            st.image(roi, use_container_width=True, caption="Smart Zoom ROI")
            st.markdown(f"<div class='metric-box'><b>Complexity Score</b><br><h2>{score:.2f}</h2></div>", unsafe_allow_html=True)
            
        with c3:
            st.markdown(f"""
                <div class="report-card">
                    <h3 style="color:#D32F2F; margin-bottom:5px;">{grade}</h3>
                    <p><b>Risk Profile:</b> {risk_level}</p>
                    <hr>
                    <p style="margin-bottom:0;"><b>Therapy Protocol:</b></p>
                    <p style="font-size:18px; color:#0A2351;"><b>{display_med}</b></p>
                    <hr>
                    <p style="margin-bottom:0;"><b>5-Year Survival:</b></p>
                    <p style="font-size:25px; color:#D32F2F;"><b>{display_surv}</b></p>
                </div>
            """, unsafe_allow_html=True)

        # Excel için veriyi hazırla (Gerçek Teşhis sütunu boş eklendi)
        summary_data.append({
            "Specimen": uploaded_file.name,
            "AI_Prediction": grade,
            "Ground_Truth_Real": "", # BURAYA EXCELDE GERÇEĞİ YAZACAKSIN
            "Therapy": display_med,
            "Survival": display_surv,
            "Complexity": round(score, 2)
        })

    # --- EXCEL RAPORU ---
    st.markdown("---")
    df = pd.DataFrame(summary_data)
    
    # Excel indirme işlemi
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 Download Clinical Report for Validation (Excel)",
        data=output.getvalue(),
        file_name="MathRIX_Validation_Report.xlsx",
        use_container_width=True
    )
