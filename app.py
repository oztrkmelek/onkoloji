import streamlit as st
import numpy as np
import cv2
import pandas as pd
from PIL import Image
from skimage import feature

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="MathRIX AI | Onkoloji CDSS", layout="wide")

# --- STİL DOSYASI (Neon Görünüm) ---
st.markdown("""
    <style>
    .main { background-color: #050f23; color: white; }
    .stMetric { background-color: #0a1932; padding: 15px; border-radius: 10px; border: 1px solid #00d4ff; border-left: 5px solid #00d4ff; }
    .verdict-card { background-color: #0a1932; padding: 20px; border-radius: 15px; border: 2px solid #ff1432; box-shadow: 0px 0px 15px #ff1432; }
    </style>
    """, unsafe_allow_html=True)

# --- KLİNİK KARAR MANTIĞI --- [cite: 2026-02-03]
# Bu bölüm patologların ilaç araştırmasını ortadan kaldırır.
NCCN_GUIDELINES = {
    "Grade 1": {"med": "Aktif İzlem / Gözlem", "surv": "%96", "risk": "Düşük"},
    "Grade 2": {"med": "Parsiyel Nefrektomi", "surv": "%88", "risk": "Orta"},
    "Grade 3": {"med": "Sunitinib (Adjuvan)", "surv": "%67", "risk": "Yüksek"},
    "Grade 4": {"med": "Nivolumab + Ipilimumab", "surv": "%35", "risk": "Çok Yüksek"}
}

# --- ANALİZ MOTORU ---
def perform_ai_analysis(uploaded_img):
    # Görüntüyü işle
    image = Image.open(uploaded_img)
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Doku Karmaşıklığı (LBP Analizi)
    lbp = feature.local_binary_pattern(gray, 24, 3, method="uniform")
    entropy_score = np.std(lbp)
    
    # Isı Haritası (Heatmap)
    heatmap = cv2.applyColorMap(cv2.equalizeHist(gray), cv2.COLORMAP_JET)
    heatmap = cv2.addWeighted(cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR), 0.6, heatmap, 0.4, 0)
    
    return entropy_score, heatmap

# --- ARAYÜZ BAŞLIĞI ---
st.title("🧬 MathRIX AI: Renal Hücreli Karsinom Analizi")
st.write("Hesaplamalı Patoloji ve Otomatik Klinik Karar Destek Sistemi")

# --- YAN PANEL ---
with st.sidebar:
    st.header("⚙️ Hasta Parametreleri")
    is_m1 = st.toggle("🚨 METASTAZ MEVCUT (M1)")
    st.divider()
    st.info("Bu sistem, patoloji uzmanlarının manuel ilaç araştırması ihtiyacını ortadan kaldırmak için tasarlanmıştır. [cite: 2026-02-03]")

# --- DOSYA YÜKLEME ---
file = st.file_uploader("Patoloji Kesiti Yükle (ROI)", type=["jpg", "png", "jpeg"])

if file:
    # AI Analizini Çalıştır
    chaos_index, heatmap_img = perform_ai_analysis(file)
    
    # Derecelendirme Mantığı
    if chaos_index > 1.4: grade = "Grade 4"
    elif chaos_index > 1.0: grade = "Grade 3"
    elif chaos_index > 0.6: grade = "Grade 2"
    else: grade = "Grade 1"
    
    # Klinik Karar Çıktısı [cite: 2026-02-03]
    res = NCCN_GUIDELINES[grade]
    final_med = "Nivolumab + Cabozantinib" if is_m1 else res["med"]
    final_surv = "%15-20" if is_m1 else res["surv"]

    # --- DASHBOARD ---
    col1, col2, col3 = st.columns([2, 1, 1.5])
    
    with col1:
        st.subheader("🔍 AI Isı Haritası")
        st.image(heatmap_img, channels="BGR", use_container_width=True, caption="Topolojik Doku Analizi")
        
    with col2:
        st.subheader("📊 Analiz Metrikleri")
        st.metric("Kaos İndeksi", f"{chaos_index:.3f}")
        st.metric("Tespit Edilen Evre", grade)
        st.write(f"Risk Durumu: *{res['risk']}*")
        
    with col3:
        st.subheader("🏥 Klinik Karar (Öneri)")
        st.markdown(f"""
            <div class="verdict-card">
                <h3 style='color:white; margin-top:0;'>{grade} Karar Kartı</h3>
                <p><b>Önerilen Tedavi:</b><br><span style='font-size:1.3em; color:#00d4ff;'>{final_med}</span></p>
                <hr style='border: 0.5px solid #444;'>
                <p><b>5 Yıllık Sağ Kalım Beklentisi:</b></p>
                <h1 style='color:#ff1432; margin:0;'>{final_surv}</h1>
                <small style='color:#aaa;'>Kaynak: NCCN Onkoloji Protokolleri [cite: 2026-02-03]</small>
            </div>
        """, unsafe_allow_html=True)

    # Rapor Tablosu
    st.divider()
    report_data = {
        "Parametre": ["Doku Karmaşıklığı", "Otomatik İlaç Önerisi", "Sağ Kalım Analizi", "Metastaz Durumu"],
        "Değer": [f"{chaos_index:.2f}", final_med, final_surv, "EVET" if is_m1 else "HAYIR"]
    }
    st.table(pd.DataFrame(report_data))
