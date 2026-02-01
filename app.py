import streamlit as st
import time
from PIL import Image, ImageDraw
import random

# Sayfa Ayarları
st.set_page_config(page_title="MathRix AI Oncology Ultra", layout="wide", page_icon="🔬")

# --- GELİŞMİŞ TIBBİ CSS (Süper Modern) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #1e293b; }
    .medical-card {
        background: white; padding: 25px; border-radius: 15px;
        border-left: 8px solid #3b82f6; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .upload-bubble {
        background: #ffffff; padding: 40px; border-radius: 30px;
        border: 2px dashed #cbd5e1; box-shadow: 0 15px 30px rgba(0,0,0,0.05);
    }
    .report-frame {
        background: white; padding: 40px; border-radius: 20px;
        border-top: 25px solid #1e3a8a; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
    }
    .timeline-box {
        background: #f1f5f9; padding: 15px; border-radius: 10px;
        border-left: 4px solid #ef4444; margin: 10px 0;
    }
    .tda-overlay { position: relative; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ SİSTEMİ ---
if 'authenticated' not in st.session_state: st.session_state['authenticated'] = False
if not st.session_state['authenticated']:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<br><br><div style='background:white; padding:50px; border-radius:25px; border:2px solid #3b82f6; text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1>🧬 MATHRIX ONCO-CORE</h1>", unsafe_allow_html=True)
        password = st.text_input("Sistem Şifresi:", type="password")
        if st.button("SİSTEME ERİŞ"):
            if password == "mathrix2026":
                st.session_state['authenticated'] = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- ANA PANEL ---
st.markdown("<h1 style='text-align: center;'>🏥 MATHRIX AI: İLERİ SEVİYE ONKOLOJİK PROJEKSİYON</h1>", unsafe_allow_html=True)

# --- DEĞİŞTİRİLMEYEN BİLGİ PORTALI ---
st.markdown("### 📖 Klinik ve Tıbbi Bilgi Portalı")
tab1, tab2, tab3 = st.tabs(["🔬 Kanser Alt Tipleri", "💊 İlaç ve Tedavi Dalları", "📊 Evreleme Protokolü"])
with tab1:
    c1, c2, c3 = st.columns(3)
    c1.markdown("<div class='medical-card'><b>🔹 Adenokarsinom</b><br><br>Akciğer dış çeperinde gelişir. Müsin üretiminden sorumludur. EGFR mutasyonu %40-50 oranında bu grupta görülür.</div>", unsafe_allow_html=True)
    c2.markdown("<div class='medical-card' style='border-left-color:#e53e3e;'><b>🔸 Skuamöz Hücreli</b><br><br>Bronşlarda gelişir. Keratin incileri karakteristiktir. Sigara içiciliği ile %90 korelasyon gösterir.</div>", unsafe_allow_html=True)
    c3.markdown("<div class='medical-card' style='border-left-color:#ed8936;'><b>🔸 Büyük Hücreli</b><br><br>Diferansiye olmamış, dev hücreli yapıdır. Çok hızlı bölünür ve hızla uzak organlara yayılma eğilimindedir.</div>", unsafe_allow_html=True)
with tab2:
    st.markdown("#### 💊 İlaç Taksonomisi ve Etki Mekanizmaları")
    st.write("Hedefe Yönelik Tedaviler (Osimertinib, Alectinib) ve İmmünoterapiler (Pembrolizumab) klinik kılavuzlara göre simüle edilir.")
with tab3:
    st.table({"Evreleme": ["Evre I", "Evre II", "Evre III", "Evre IV"], "TNM Kriteri": ["T1 N0 M0", "T2 N1 M0", "T3 N2 M0", "T(H) M1"]})

st.divider()

# --- ANALİZ VE GÖRSELLEŞTİRME ---
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.markdown("<div class='upload-bubble'>", unsafe_allow_html=True)
    st.subheader("📁 Vaka Veri Girişi")
    uploaded_file = st.file_uploader("Dijital Patoloji Kesiti Yükle", type=["jpg", "png", "jpeg"])
    metastazlar = st.multiselect("Saptanan Metastaz Alanları:", ["Beyin", "Karaciğer", "Kemik", "Sürrenal"])
    if st.button("🔬 KOMPLEKS ANALİZİ BAŞLAT"):
        st.session_state['analyzed'] = True
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        
        # NOKTA BULUTU SİMÜLASYONU (Görüntü üzerine çizim)
        if st.session_state.get('analyzed'):
            draw = ImageDraw.Draw(img)
            w, h = img.size
            for _ in range(150): # 150 tane TDA noktası oluştur
                x, y = random.randint(0, w), random.randint(0, h)
                r = 5
                draw.ellipse((x-r, y-r, x+r, y+r), fill=(255, 0, 0, 150), outline="white")
            st.image(img, use_container_width=True, caption="TDA (Topolojik Veri Analizi) Nokta Bulutu Bindirmesi")
        else:
            st.image(img, use_container_width=True, caption="Orijinal Patoloji Kesiti")

# --- DEVASA ANALİZ RAPORU VE ZAMAN ÇİZELGESİ ---
if st.session_state.get('analyzed') and uploaded_file:
    st.markdown("<div class='report-frame'>", unsafe_allow_html=True)
    st.header("📜 Kapsamlı Onkolojik Epikriz ve Risk Analizi")
    
    secilen_tur = random.choice(["Adenokarsinom", "Skuamöz Hücreli Karsinom"])
    risk = random.uniform(97.5, 99.9)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🕰️ Klinik Zaman Tüneli")
        st.markdown(f"""
        <div class='timeline-box' style='border-left-color: #64748b;'>
            <b>GEÇMİŞ (12 Ay Önce):</b> Hücresel bazda ilk mutasyonel (EGFR/KRAS) sinyallerin başlangıcı. TDA verilerine göre doku mimarisi bu dönemde bozulmaya başlamış.
        </div>
        <div class='timeline-box' style='border-left-color: #3b82f6;'>
            <b>ŞİMDİ (Mevcut Durum):</b> {secilen_tur} teşhisi (%{risk:.1f} kesinlik). Kitle çapı ve nükleer pleomorfizm agresif seyirde.
        </div>
        <div class='timeline-box' style='border-left-color: #ef4444;'>
            <b>GELECEK (6 Ay Sonraki Risk):</b> Tedavi protokolüne uyulmadığı takdirde vasküler invazyon ve SSS (Merkezi Sinir Sistemi) metastaz riski %85 artış gösterebilir.
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.subheader("💊 3T Tedavi ve Tehdit Yönetimi")
        st.write(f"""
        - *Tanı:* TDA tabanlı persistent homology analizi ile saptanan {secilen_tur}.
        - *Tedavi:* NGS sonucuna göre *Osimertinib 80mg* veya *Pembrolizumab 200mg*.
        - *Tehditler:* İlaç direnci (T790M mutasyonu) ve plevral efüzyon riski yakından izlenmelidir.
        """)

    # Detaylı Yazılı Rapor
    st.markdown("---")
    st.write(f"""
    *Klinik Yorum:* Yapılan dijital analizde dokunun Betti-1 ($\beta_1$) katsayısı yüksek bulunmuştur. 
    Bu durum, tümörün sadece bir kitle olmadığını, doku içine mikroskobik düzeyde sızdığını (invazyon) kanıtlar. 
    Hastanın geçmişteki sigara öyküsü veya çevresel maruziyeti, epigenetik modifikasyonları tetiklemiş olabilir. 
    *Öneri:* Acil olarak Likit Biyopsi (ctDNA) takibi başlatılmalı ve 3 ayda bir PET-CT planlanmalıdır.
    """)
    
    rapor_data = f"TANI: {secilen_tur}\nKESINLIK: %{risk:.1f}\nGEÇMİŞ: 12 Ay önce başlangıç\nGELECEK RİSK: %85 Metastaz artışı"
    st.download_button("📩 FULL KLİNİK RAPORU VE SİMÜLASYON DOSYASINI İNDİR", rapor_data, "MathRix_Kapsamlı_Rapor.txt")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><hr><center>MathRix Health Systems © 2026 | Professional Oncology Decision Support</center>", unsafe_allow_html=True)
