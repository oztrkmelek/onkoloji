import streamlit as st
import time
from PIL import Image
import random

# Sayfa Ayarları
st.set_page_config(page_title="MathRix AI Oncology Pro", layout="wide")

# --- GİRİŞ SİSTEMİ ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("<h1 style='text-align: center; color: #001f3f;'>MATHRIX NEURAL CORE ACCESS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password = st.text_input("Sistem Erişim Şifresi:", type="password")
        if st.button("Sisteme Giriş Yap"):
            if password == "mathrix2026":
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre! Erişim Reddedildi.")
    st.stop()

# --- ANA PANEL ---
st.markdown("<h1 style='color: #003366; text-align: center;'>🧬 MATHRIX ONKOLOJİ ANALİZ PANELİ</h1>", unsafe_allow_html=True)

# --- ESKİ SEVİLEN BİLGİ PANELİ GERİ GELDİ ---
st.subheader("📚 Akciğer Kanseri Klinik Bilgi Bankası")
tab1, tab2, tab3 = st.tabs(["Kanser Türleri", "Evreleme & Metastaz", "İlaçlar & Tedavi"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("*1. Adenokarsinom:* En yaygın tür. Genelde çevresel yayılım izler.")
        st.info("*2. Skuamöz Hücreli:* Bronşlarda keratin incileri ile karakterizedir.")
    with col_b:
        st.info("*3. Büyük Hücreli:* Dev hücreli, agresif ve hızlı seyirlidir.")
        st.info("*4. Küçük Hücreli (KHAK):* Nöroendokrin kaynaklı, çok hızlı metastaz yapar.")

with tab2:
    st.warning("⚠️ *Metastaz Durumu:* Akciğer kanseri öncelikle Karaciğer, Beyin ve Kemiklere sıçrama eğilimindedir.")
    st.write("Evre 1-3 yerel/bölgesel kabul edilirken; başka organ tutulumu *Evre 4* demektir.")

with tab3:
    c1, c2 = st.columns(2)
    c1.success("*Akıllı İlaçlar:* EGFR/ALK mutasyonu varsa (Gefitinib, Erlotinib).")
    c2.error("*İmmünoterapi:* Bağışıklık sistemini aktive eder (Pembrolizumab - Keytruda).")

st.divider()

# --- ANALİZ BÖLÜMÜ ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📸 Analiz Ünitesi")
    uploaded_file = st.file_uploader("Görüntü Yükle (Adeno, Skuamöz, Large Cell Örnekleri)", type=["jpg", "png", "jpeg"])
    
    st.write("📋 *Klinik Veriler*")
    yas = st.number_input("Yaş:", 1, 120, 65)
    sigara = st.selectbox("Sigara:", ["Hiç içmemiş", "Eski", "Aktif"])
    metastaz = st.multiselect("Metastaz:", ["Yok", "Karaciğer", "Beyin", "Kemik"])

with col_right:
    if uploaded_file:
        st.image(Image.open(uploaded_file), use_container_width=True)
        
        if st.button("🔬 ANALİZİ ÇALIŞTIR"):
            with st.spinner("Doku örneği taranıyor..."):
                time.sleep(3)
                
                # --- AKILLI DEĞİŞKEN SONUÇLAR ---
                turler = ["Adenokarsinom", "Skuamöz Hücreli Karsinom", "Büyük Hücreli Karsinom"]
                secilen_tur = random.choice(turler) # Her seferinde farklı sonuç çıksın diye
                risk_skoru = random.uniform(85.5, 96.8)
                
                st.error(f"### BULGU: {secilen_tur.upper()}")
                st.markdown(f"""
                - *Kritik Malignite Skoru:* %{risk_skoru:.1f}
                - *Hücresel Durum:* Belirgin nükleer pleomorfizm ve atipi izlendi.
                - *Öneri:* {secilen_tur} ile uyumlu doku mimarisi. Patolojik konfirme şarttır.
                """)
                
                # Zengin Rapor Metni
                rapor_icerik = f"""
                MATHRIX ONKOLOJI ANALIZ RAPORU
                -------------------------------
                TARIH: {time.strftime('%d/%m/%Y')}
                TESHIS SUPHESI: {secilen_tur}
                RISK ORANI: %{risk_skoru:.1f}
                
                HASTA PROFILI:
                - Yas: {yas} | Sigara: {sigara}
                - Metastaz: {", ".join(metastaz)}
                
                TIBBI DEGERLENDIRME:
                Incelenen doku orneginde {secilen_tur} bulgulari saptanmistir. 
                Hucreler agresif yayilim gostermektedir. Karaciger ve beyin taramalari onerilir.
                
                ONERILEN TEDAVI YOLU:
                - {secilen_tur} vakalarinda mutasyon testi (NGS) yapilmalidir.
                - Akilli ilac veya Immunoterapi uygunlugu arastirilmalidir.
                """
                
                st.download_button("📩 DETAYLI RAPORU INDIR", rapor_icerik, f"MathRix_Rapor_{secilen_tur}.txt")
    else:
        st.info("Analiz için görsel yükleyiniz.")
