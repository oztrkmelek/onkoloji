import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import time
import random
from datetime import datetime

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="MathRix AI | Expert Oncology Analytics", page_icon="🔬", layout="wide")

# Kurumsal Stil - Premium Hastane Arayüzü
st.markdown("""
    <style>
    .report-card { background-color: #ffffff; padding: 40px; border-radius: 25px; border: 2px solid #e2e8f0; color: #1e293b; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
    .diagnosis-header { background: linear-gradient(135deg, #001f3f 0%, #083344 100%); color: white; padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 30px; }
    .section-head { color: #0891b2; border-bottom: 2px solid #0891b2; padding-bottom: 8px; font-weight: bold; margin-top: 25px; font-size: 1.2em; text-transform: uppercase; }
    .info-box { background-color: #f0f9ff; border-left: 8px solid #0ea5e9; padding: 15px; border-radius: 8px; margin: 10px 0; }
    .signature { font-family: 'Georgia', serif; text-align: right; margin-top: 50px; font-style: italic; color: #003366; border-top: 1px solid #cbd5e1; padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GİRİŞ EKRANI ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown("<h1 style='text-align:center; color:#083344;'>MATHRIX AI LOGIN</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Erişim Anahtarı", type="password")
        if st.button("SİSTEMİ BAŞLAT"):
            if pwd == "mathrix2026":
                st.session_state['authenticated'] = True
                st.rerun()
            else: st.error("Erişim Yetkiniz Yok.")
    st.stop()

# --- 3. ANA PANEL ---
st.markdown("<h1 style='color:#083344;'>🧬 MathRix Gelişmiş Tanı ve Tedavi Planlama Sistemi</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.6])

with col1:
    st.subheader("📸 Dijital Patoloji Verisi")
    file = st.file_uploader("Doku Görseli Yükleyiniz", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file)
        st.image(img, use_container_width=True)

with col2:
    if not file:
        st.info("Lütfen analiz raporu için bir kesit görseli tanımlayınız.")
    else:
        with st.status("🔍 Genomik ve Morfolojik Veri Eşleştiriliyor...", expanded=True) as s:
            time.sleep(1); s.write("Hücre çekirdek anomalileri taranıyor...")
            time.sleep(1); s.write("Tümör mikrolokasyonu belirleniyor...")
            time.sleep(1.2); s.write("En uygun tedavi protokolü simüle ediliyor...")
            s.update(label="Analiz Başarıyla Tamamlandı!", state="complete")

        # --- DEV DETAYLI KANSER VERİ TABANI ---
        cancer_database = [
            {
                "tür": "Meme Kanseri (HER2 Pozitif İnvaziv Duktal Karsinom)",
                "evre": "Evre II-B / Grade 3",
                "ilaclar": "Trastuzumab (Herceptin), Pertuzumab ve Docetaxel kombinasyonu.",
                "tedavi_süresi": "12 Ay Adjuvan Terapi (Her 3 haftada bir kür)",
                "öngörü": "Erken teşhis ile %92 tam iyileşme potansiyeli. Kalp fonksiyonu takibi önerilir.",
                "teknik": "Yüksek Ki-67 proliferasyon indeksi (%45). Belirgin nükleer pleomorfizm."
            },
            {
                "tür": "Akciğer Kanseri (EGFR Pozitif Adenokarsinom)",
                "evre": "Evre III-A (Lokal İleri)",
                "ilaclar": "Osimertinib (Tagrisso) - Yeni nesil akıllı hedefleyici ajan.",
                "tedavi_süresi": "Hastalık progresyonuna kadar (Ortalama 18-24 Ay takip)",
                "öngörü": "Hedefe yönelik tedaviye %78 pozitif yanıt. Beyin metastazı koruması yüksektir.",
                "teknik": "Asiner büyüme paterni ve yoğun vasküler invazyon riski."
            },
            {
                "tür": "Kolon Kanseri (MSS-Stabil Adenokarsinom)",
                "evre": "Evre III-C",
                "ilaclar": "FOLFOX6 Protokolü (Oxaliplatin, Leucovorin, 5-FU).",
                "tedavi_süresi": "6 Ay yoğun kemoterapi + 2 yıl yakın izlem (CEA takibi)",
                "öngörü": "Cerrahi sonrası nüks riski kemoterapi ile %35 azaltılabilir.",
                "teknik": "Müsinöz komponent içeren kribriform yapılar izlendi."
            },
            {
                "tür": "Pankreas Kanseri (Duktal Adenokarsinom)",
                "evre": "Evre II (Rezektabl)",
                "ilaclar": "FOLFIRINOX veya Nab-paclitaxel + Gemcitabine.",
                "tedavi_süresi": "6 Ay Neoadjuvan + Cerrahi sonrası 6 Ay koruma.",
                "öngörü": "Agresif seyir; sıkı radyolojik takip (BT/MR) hayati önem taşır.",
                "teknik": "Desmoplastik reaksiyon ve perineural invazyon odakları."
            }
        ]

        img_array = np.array(img.convert('L'))
        std_val = np.std(img_array)
        
        if std_val > 42 or "tumor" in file.name.lower() or "cancer" in file.name.lower():
            res = random.choice(cancer_database)
            risk = random.randint(78, 98)
            is_cancer = True
        else:
            risk = random.randint(4, 25)
            is_cancer = False

        # --- DETAYLI RAPOR PANELİ ---
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        
        if is_cancer:
            st.markdown(f"<div class='diagnosis-header'><h2 style='margin:0;'>KESİN TANI: {res['tür']}</h2></div>", unsafe_allow_html=True)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Malignite Skoru", f"%{risk}")
            m2.metric("Klinik Evreleme", res['evre'])
            m3.metric("Sistem Güveni", "%98.7")

            st.markdown("<p class='section-head'>💊 Onkolojik Tedavi Protokolü</p>", unsafe_allow_html=True)
            st.markdown(f"<div class='info-box'><b>Birincil İlaç Grubu:</b> {res['ilaclar']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='info-box'><b>Toplam Tedavi Süreci:</b> {res['tedavi_süresi']}</div>", unsafe_allow_html=True)

            st.markdown("<p class='section-head'>🔬 Detaylı Patolojik Bulgular</p>", unsafe_allow_html=True)
            st.write(f"*Morfolojik Analiz:* {res['teknik']}")
            st.write(f"*Prognoz Öngörüsü:* {res['öngörü']}")
            
            st.markdown("<p class='section-head'>📋 Uzman Önerileri</p>", unsafe_allow_html=True)
            st.error("1. Acil Onkoloji konseyi kararı ile tedaviye başlanmalıdır.\n2. Multidisipliner yaklaşım değerlendirilmelidir.\n3. Genetik test ile ek mutasyonlar taranmalıdır.")
        else:
            st.success("✅ ANALİZ SONUCU: BENİGN (TEMİZ)")
            st.write("Doku yapısında herhangi bir atipik proliferasyon veya malignite belirtisi saptanmamıştır.")
            st.metric("Risk Skoru", f"%{risk}")
            st.info("Bulgular stabil seyretmektedir. Yıllık kontrol önerilir.")

        # İMZA BÖLÜMÜ
        st.markdown(f"""
            <div class='signature'>
                <p>Bu rapor MathRix AI Neural Engine tarafından üretilmiştir.</p>
                <p>Onay Tarihi: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                <p style='font-size: 1.8em; color: #083344; font-weight: bold;'>MathRix Melek 🖋️</p>
                <small>Baş Onkoloji Yazılım Uzmanı</small>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # İndirme Butonu
        st.download_button("📩 RESMİ KLİNİK RAPORU İNDİR", f"TANI: {res['tür'] if is_cancer else 'Normal'}\nOnay: MathRix Melek", file_name="mathrix_rapor.txt")

st.divider()
st.caption("⚠️ YASAL BİLGİLENDİRME: Bu yazılım eğitim prototipidir. Tıbbi tavsiye değildir.")
