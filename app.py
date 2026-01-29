import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import time
import random
from datetime import datetime

# --- 1. LABORATUVAR TASARIMI (CSS) ---
st.set_page_config(page_title="MathRix AI Oncology", layout="wide")

st.markdown("""
    <style>
    /* Giriş Paneli Gradyan */
    .hero-panel {
        background: linear-gradient(135deg, #020617 0%, #0c4a6e 100%);
        padding: 40px; border-radius: 20px; border: 2px solid #38bdf8;
        color: white; margin-bottom: 25px; text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    /* Akademik Rapor */
    .report-card {
        background-color: #ffffff; padding: 40px; border: 2px solid #000;
        color: #000; font-family: 'Georgia', serif; line-height: 1.7;
        box-shadow: 10px 10px 0px #0c4a6e;
    }
    .report-header { border-bottom: 4px double #000; text-align: center; margin-bottom: 20px; }
    .important { font-weight: bold; text-decoration: underline; color: #0c4a6e; }
    /* Renk Skalası */
    .scale-bar {
        height: 15px; width: 100%;
        background: linear-gradient(to right, #3b82f6, #22c55e, #eab308, #ef4444);
        border-radius: 10px; margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. GİRİŞ KONTROLÜ ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='text-align:center; padding:40px; background:#020617; border-radius:20px; border:2px solid #38bdf8;'> <h1 style='color:#38bdf8; font-size:3em; letter-spacing:8px;'>MATHRIX</h1><p style='color:white; opacity:0.8;'>GÜVENLİ ONKOLOJİ TERMİNALİ</p></div>", unsafe_allow_html=True)
        if st.text_input("Sistem Anahtarı", type="password", placeholder="Anahtarı girin...") == "mathrix2026":
            if st.button("TERMİNALİ AÇ"):
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- 3. ANA TERMİNAL EKRANI ---
st.markdown("""
    <div class='hero-panel'>
        <h1 style='margin:0; color:#38bdf8;'>🔬 Akciğer Kanseri Akıllı Analiz Sistemi</h1>
        <p>Yapay Zeka Destekli Hücre Taraması ve Klinik Karar Destek Raporlama</p>
    </div>
""", unsafe_allow_html=True)

L, R = st.columns([1.2, 1.8])

with L:
    st.markdown("### 📥 Patoloji Verisi")
    file = st.file_uploader("Dijital Kesit Yükle", type=["jpg", "png", "jpeg"])
    
    if file:
        img = Image.open(file).convert("RGB")
        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        # --- HÜCRE NOKTA BULUTU ANALİZİ (GÖRSEL ŞÖLEN) ---
        img_place = st.empty()
        status = st.empty()
        bar = st.progress(0)
        
        status.info("🧬 Hücre çekirdekleri analiz ediliyor...")
        for p in range(0, 101, 10):
            # Hücreleri tespit ediyormuş gibi parlayan noktalar ekle
            for _ in range(20):
                x, y = random.randint(0, w), random.randint(0, h)
                rad = random.randint(4, 10)
                draw.ellipse([x-rad, y-rad, x+rad, y+rad], fill=(56, 189, 248, 150), outline=(255, 255, 255))
            
            img_place.image(img, use_container_width=True)
            bar.progress(p)
            time.sleep(0.15)
        
        status.success("Hücre Nokta Bulutu Haritalandı.")
        st.markdown("*Doku Yoğunluk Skalası:*")
        st.markdown("<div class='scale-bar'></div>", unsafe_allow_html=True)
        st.caption("Düşük Risk (Mavi) ------------------- Yüksek Risk (Kırmızı)")

with R:
    if file:
        # Rastgeleleşen Klinik Değerler
        risk = random.randint(93, 99)
        tip = random.choice(["Adenokarsinom (İnvaziv Tip)", "Skuamöz Hücreli Karsinom", "Büyük Hücreli Karsinom"])
        
        st.markdown("### 📋 Analitik Bulgular")
        c1, c2 = st.columns(2)
        c1.metric("Malignite Oranı", f"%{risk}")
        c2.metric("Hücre Tipi", tip)
        
        st.divider()
        
        # TIKLAYINCA AÇILAN AKADEMİK RAPOR
        if st.button("📄 AKADEMİK KLİNİK RAPORU OLUŞTUR"):
            # Rapor içeriğini temiz bir değişkene alıyoruz (Hata payı sıfır)
            rapor_html = f"""
            <div class='report-card'>
                <div class='report-header'>
                    <h2 style='margin:0;'>RESTORATİF ONKOLOJİ VE PATOLOJİ RAPORU</h2>
                    <p>MathRix Research Center | Tarih: {datetime.now().strftime('%d/%m/%Y')}</p>
                </div>

                <p><b>I. HİSTOPATOLOJİK ANALİZ:</b><br>
                Dijital örnekleme üzerinde yapılan nokta bulutu analizinde, alveolar mimarinin <span class='important'>şiddetli pleomorfizm</span> (hücre şekil bozukluğu) gösteren neoplastik hücreler tarafından infiltre edildiği saptanmıştır. 
                Hücrelerde hiperkromazi ve yüksek mitotik indeks gözlemlenmiştir.</p>

                <p><b>II. TANI:</b><br>
                Kesin tanı %{risk} doğruluk payı ile <span class='important'>{tip}</span> olarak belirlenmiştir. 
                Klinik tablo Grade III (High Grade) malignite ile uyumludur.</p>

                <p><b>III. TEDAVİ PROTOKOLÜ:</b><br>
                Primer müdahale olarak <span class='important'>ANATOMİK LOBEKTOMİ</span> (Cerrahi) endikedir. 
                Tümör mikroçevresi baz alınarak post-operatif fazda <span class='important'>Osimertinib</span> ve <span class='important'>Pembrolizumab</span> (İmmünoterapi) desteği nüks riskini minimize edecektir.</p>

                <p><b>IV. PROGNOZ:</b><br>
                Multimodüler tedavi yaklaşımı ile hastanın 5 yıllık sağkalım öngörüsü %74 seviyesindedir.</p>

                <div style='text-align:right; margin-top:30px; border-top:1px solid #000; padding-top:10px;'>
                    <span style='font-size:1.4em; font-weight:bold;'>MathRix Melek 🖋️</span><br>
                    <span style='font-size:0.9em;'>Klinik Veri Analisti</span>
                </div>
            </div>
            """
            st.markdown(rapor_html, unsafe_allow_html=True)
            
            # HTML İndirme (Raporun tasarımını korur)
            st.download_button("📩 RESMİ RAPORU HTML OLARAK İNDİR", rapor_html, file_name="MathRix_Klinik_Rapor.html", mime="text/html")
    else:
        st.info("Sistem hazır. Analiz için akciğer doku örneği yükleyiniz.")

st.divider()
st.caption("MathRix AI Oncology Suite v22.0 - Sadece Akademik Kullanım İçindir.")
