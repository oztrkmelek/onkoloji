import streamlit as st
import numpy as np
import pandas as pd
import io
from datetime import datetime
from PIL import Image
from skimage import color, feature, filters, util, measure

# --- ACADEMIC KNOWLEDGE BASE v7.0 (2025-2026 Focus) ---
CLINICAL_KNOWLEDGE = {
    "Inflammation_Impact": "Tumor mikroçevresindeki kronik inflamasyon (iltihap), nüks riskini artırabilir ve daha sıkı takip protokolleri gerektirebilir.",
    "irAE_Monitoring": {
        "Colitis": "Semptomlar: Diyare, kanlı dışkı. Yönetim: IO kesilir, Steroid başlanır.",
        "Hepatitis": "Semptomlar: Sarılık, LFT yüksekliği. Yönetim: Hepatoloji konsültasyonu."
    },
    "Grade_Protocols": {
        "Grade 1": {"Diag": "Low Neoplastic Complexity", "OS": ">95%", "Surgical": "Partial Nephrectomy (PN)", "Complications": "Minor Hemorrhage risk"},
        "Grade 2": {"Diag": "Intermediate Complexity", "OS": "~85-90%", "Surgical": "PN + Adjuvant IO if high risk", "Complications": "Urinary fistula risk"},
        "Grade 3": {"Diag": "High Neoplastic Complexity", "OS": "~65-70%", "Surgical": "Radical Nephrectomy + Adjuvant Pembrolizumab", "Complications": "DVT risk"},
        "Grade 4": {"Diag": "Aggressive / Sarcomatoid", "OS": "<50%", "Surgical": "Radical Nephrectomy + Caval Thrombectomy", "Complications": "PE / Major Hemorrhage risk"},
        "Stage IV": {"Diag": "Metastatic RCC", "OS": "Variable", "Med": "Dual IO (Nivo+Ipi) or IO-TKI", "irAE": "High Monitor Required"}
    }
}

# --- ENSEMBLE VISION ENGINE v7.0 ---
def run_v7_vision_engine(image_rgb):
    gray = color.rgb2gray(image_rgb)
    sharpened = filters.unsharp_mask(gray, radius=1.0, amount=1.5)
    u_img = util.img_as_ubyte(sharpened)

    # Hybrid GLCM Features
    glcm = feature.graycomatrix(u_img, [1, 3], [0, np.pi/2], 256, symmetric=True, normed=True)
    contrast = feature.graycoprops(glcm, 'contrast').mean()
    asm = feature.graycoprops(glcm, 'ASM').mean()
    correlation = feature.graycoprops(glcm, 'correlation').mean()

    # Entropy & Inflammation Detection
    ent = measure.shannon_entropy(gray)
    lap = filters.laplace(gray)
    inflam_score = np.var(lap) * 1000
    inflammation_detected = inflam_score > 15.0

    # Weighted Ensemble Scoring
    n_contrast = np.clip(contrast / 500, 0, 1)
    score = (n_contrast * 0.5 + (1 - asm) * 0.3 + (1 - (correlation+1)/2) * 0.2) * 100

    if score > 80: grade = "Grade 4"
    elif score > 55: grade = "Grade 3"
    elif score > 30: grade = "Grade 2"
    else: grade = "Grade 1"

    risk_map = filters.gaussian(np.abs(lap), sigma=3)
    risk_map = (risk_map - risk_map.min()) / (risk_map.max() - risk_map.min() + 1e-8)

    return grade, risk_map, {'Score': score, 'Contrast': contrast, 'ASM': asm, 'Inflammation': inflammation_detected}

# --- STREAMLIT UI v7.0 ---
st.set_page_config(page_title="MathRIX AI v7.0", page_icon="⚕", layout="wide")

# User Session & Audit Log Initialization
if "user_identity" not in st.session_state:
    st.session_state.user_identity = None
    st.session_state.session_start = None

if st.session_state.user_identity is None:
    st.title("⚕ MathRIX AI v7.0 - Authentication")
    with st.form("login"):
        u_name = st.text_input("Kullanıcı Ad Soyad", placeholder="Örn: Ahmet Yılmaz")
        if st.form_submit_button("Sisteme Giriş Yap"):
            if u_name:
                st.session_state.user_identity = u_name
                st.session_state.session_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.rerun()
            else: st.warning("Denetim kaydı için isim gereklidir.")
    st.stop()

# Sidebar - Audit & Patient Info
st.sidebar.markdown(f"### ⚕ MathRIX AI v7.0\n**Kullanıcı:** {st.session_state.user_identity}\n**Giriş:** {st.session_state.session_start}")
st.sidebar.divider()
with st.sidebar.expander("Hasta Dosyası", expanded=True):
    pid = st.text_input("Hasta ID", "RCC-2026-V7")
    m1_check = st.toggle("M1 Metastatik Override", value=False)
    gtruth = st.selectbox("Patolog Doğrulaması", ["Grade 1", "Grade 2", "Grade 3", "Grade 4"])

# Main Dashboard
st.title("Digital Pathology Oncology Dashboard v7.0")
st.markdown("--- clinical diagnostics based on 2025-2026 standards ---")

upload = st.file_uploader("Patoloji Görüntüsü Yükle (H&E)", type=['png', 'jpg', 'jpeg', 'tif'])

if upload:
    img_raw = Image.open(upload).convert("RGB")
    
    with st.spinner("Gelişmiş Analiz Yapılıyor..."):
        grade, risk_map, m = run_v7_vision_engine(np.array(img_raw))

    # Logic: Clinical Mapping
    key = "Stage IV" if m1_check else grade
    proto = CLINICAL_KNOWLEDGE["Grade_Protocols"][key]

    tab1, tab2 = st.tabs(["🔬 Diagnostic Vision", "🛡 Clinical Protocols"])

    with tab1:
        col1, col2, col3 = st.columns(3)
        col1.metric("AI Grade Tahmini", grade)
        col2.metric("İltihap (Inflammation)", "POZİTİF" if m['Inflammation'] else "DÜŞÜK")
        col3.metric("Hybrid Güven Skoru", f"{m['Score']:.2f}")

        if m['Inflammation']: st.warning(f"**Klinik Uyarı:** {CLINICAL_KNOWLEDGE['Inflammation_Impact']}")

        st.subheader("Görsel Analiz ve Risk Haritalama")
        zoom = st.slider("Görüntü Yakınlaştırma", 400, 1200, 600)
        v1, v2 = st.columns(2)
        v1.image(img_raw, caption="Orijinal Slayt", width=zoom)
        v2.image(risk_map, caption="Topolojik Risk Haritası", width=zoom, clamp=True)

    with tab2:
        st.header(f"Klinik Yönetim: {key}")
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Cerrahi & Adjuvan Plan")
            st.write(f"**Öneri:** {proto.get('Surgical', proto.get('Med'))}")
            st.write(f"**Komplikasyon Riski:** {proto.get('Complications', 'N/A')}")
        with c2:
            st.subheader("Sağkalım & İzlem")
            st.write(f"**5 Yıllık OS:** {proto['OS']}")
            if "irAE" in proto: st.info(f"**irAE Notu:** {proto['irAE']}")

    # Professional Audit Report
    report_df = pd.DataFrame({
        "Denetleyen": [st.session_state.user_identity],
        "Oturum_Zamani": [st.session_state.session_start],
        "Hasta_ID": [pid],
        "AI_Grade": [grade],
        "Gercek_Grade": [gtruth],
        "Iltihap_Durumu": ["Pozitif" if m['Inflammation'] else "Negatif"],
        "Hybrid_Skor": [f"{m['Score']:.4f}"],
        "Tedavi_Onerisi": [proto.get('Med', proto.get('Surgical'))]
    })

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, index=False, sheet_name='Audit_Report')

    st.sidebar.download_button(
        label="📥 Denetim Raporunu İndir (Excel)",
        data=buffer.getvalue(),
        file_name=f"MathRIX_Audit_v7_{pid}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Analizi başlatmak için lütfen bir histoloji görüntüsü yükleyin.")
    
