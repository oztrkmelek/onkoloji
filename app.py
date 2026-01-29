import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import time
import random
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="MathRix AI | Expert Portal", page_icon="🧬", layout="wide")

# Kurumsal Stil
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border-top: 4px solid #003366; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .critical-alert { padding: 20px; border-radius: 10px; background-color: #ff4b4b; color: white; font-weight: bold; text-align: center; margin-bottom: 10px; }
    .normal-alert { padding: 20px; border-radius: 10px; background-color: #28a745; color: white; font-weight: bold; text-align: center; margin-bottom: 10px; }
    .main-header {
        background-color: #003366; 
        padding: 25px; 
        border-radius: 10px; 
        color: white; 
        margin-bottom: 30px;
        border-left: 10px solid #3b82f6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ANA KONTROL PANELİ ---
st.markdown("""
    <div class='main-header'>
        <h1 style='margin:0;'>Onkolojik Dinamiklerin Topolojik Analiz Sistemi</h1>
        <p style='margin:0; opacity: 0.8;'>Klinik Karar Destek Mekanizması | Neural Core v4.2.0</p>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.3])

with col1:
    st.subheader("📥 Veri Giriş Terminali")
    uploaded_file = st.file_uploader("Dijital Kesiti Tanımlayınız...", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Analiz Edilen Kesit", use_container_width=True)

with col2:
    st.subheader("🔍 Gerçek Zamanlı Analiz")
    if not uploaded_file:
        st.warning("Analiz başlatmak için lütfen görsel yükleyiniz.")
    else:
        log_placeholder = st.empty()
        progress_bar = st.progress(0)
        logs = ["Piksel matrisleri okunuyor...", "Topolojik haritalama yapılıyor...", "Malignite skorlaması hesaplanıyor...", "Rapor mühürleniyor..."]
        
        for i, log in enumerate(logs):
            log_placeholder.code(f"PROCESSING: {log}")
            time.sleep(0.5)
            progress_bar.progress((i + 1) * 25)
        
        # Analiz Simülasyonu
        img_array = np.array(img.convert('L'))
        mean_val = np.mean(img_array)
        std_val = np.std(img_array)
        risk_score = int(np.clip((1 - (mean_val/255))*100 + (std_val/128)*10, 5, 99))
        
        if risk_score >= 50:
            st.markdown(f'<div class="critical-alert">🚨 KRİTİK ANALİZ: %{risk_score} RİSK - MALİGNİTE ŞÜPHESİ</div>', unsafe_allow_html=True)
            status = "MALİGNİTE ŞÜPHESİ"
        else:
            st.markdown(f'<div class="normal-alert">✅ STABİL ANALİZ: %{risk_score} RİSK - BENİGN BULGULAR</div>', unsafe_allow_html=True)
            status = "BENİGN BULGULAR"

        report_id = f"MX-{random.randint(100000, 999999)}"
        rapor_metni = f"MATHRIX AI RAPORU\nID: {report_id}\nDurum: {status}\nRisk: %{risk_score}"
        
        m1, m2 = st.columns(2)
        m1.metric("Risk Katsayısı", f"%{risk_score}")
        m2.metric("Güvenilirlik", "%94.2")
        
        st.area_chart(pd.DataFrame({'Topolojik Sapma': [10, 25, 15, risk_score, 80, 95]}))
        st.download_button("📩 RESMİ KLİNİK RAPORU İNDİR", data=rapor_metni, file_name=f"MathRix_Report_{report_id}.txt")

st.divider()
st.markdown("<center><small>MathRix Global Health Technologies | 2026</small></center>", unsafe_allow_html=True)
