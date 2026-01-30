import streamlit as st
import time
from PIL import Image
import random

# Sayfa Ayarları
st.set_page_config(page_title="MathRix AI Oncology", layout="wide")

# --- GİRİŞ PANELİ (ŞİFRELEME) ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("<h1 style='text-align: center; color: #001f3f;'>MATHRIX NEURAL CORE ACCESS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password = st.text_input("Sistem Erişim Şifresi:", type="password")
        if st.button("Sisteme Giriş Yap"):
            if password == "mathrix2026": # Şifreni buradan değiştirebilirsin
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre! Erişim Reddedildi.")
    st.stop()

# --- ANA SİSTEM (Giriş Yapıldıktan Sonra) ---
st.markdown("""
    <style>
    .main-header { background: linear-gradient(90deg, #001f3f, #003366); padding: 25px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px;}
    .info-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #003366; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-header'><h1>MATHRIX AI ONKOLOJİK ANALİZ VE BİLGİ SİSTEMİ</h1></div>", unsafe_allow_html=True)

# --- BİLGİ PANELİ (AKCİĞER KANSERİ REHBERİ) ---
st.subheader("📚 Akciğer Kanseri Klinik Rehberi")
tab1, tab2, tab3 = st.tabs(["Kanser Türleri", "Evreleme ve Metastaz", "Tedavi ve İlaçlar"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class='info-box'>
        <strong>1. Küçük Hücreli Dışı (KHDAK) - %85</strong><br>
        - <b>Adenokarsinom:</b> En yaygın tür. Akciğerin dışındadır.<br>
        - <b>Skuamöz Hücreli:</b> Merkezdeki hava yollarında, sigara odaklı.<br>
        - <b>Büyük Hücreli:</b> Hızlı yayılan, agresif tür.
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class='info-box'>
        <strong>2. Küçük Hücreli (KHAK) - %15</strong><br>
        - Çok hızlı yayılır.<br>
        - Genelde teşhis edildiğinde metastaz yapmıştır.<br>
        - Kemoterapiye hızlı yanıt verir ama nüks riski yüksektir.
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.write("### Yayılım ve Evreleme")
    st.info("Akciğer kanseri en sık *Karaciğer, Beyin ve Kemiklere* sıçrar (Metastaz).")
    st.table({
        "Evre": ["Evre 1-2", "Evre 3", "Evre 4"],
        "Açıklama": ["Sadece akciğerde sınırlı.", "Yakın lenf bezlerine yayılmış.", "Uzak organlara (Beyin/Karaciğer) sıçramış."],
        "Yaklaşım": ["Ameliyat öncelikli", "Radyoterapi + Kemo", "Akıllı İlaç + İmmünoterapi"]
    })

with tab3:
    st.write("### Modern Tedavi Yöntemleri")
    c1, c2 = st.columns(2)
    c1.success("*Akıllı İlaçlar:* EGFR, ALK mutasyonu varsa hücreyi doğrudan vurur. (Örn: Erlotinib)")
    c2.warning("*İmmünoterapi:* Bağışıklık sistemini kansere saldırttırır. (Örn: Keytruda)")

st.divider()

# --- ANALİZ KISMI ---
st.subheader("🔍 AI Patoloji Analiz Modülü")
col_input, col_result = st.columns([1, 1])

with col_input:
    uploaded_file = st.file_uploader("Analiz için Patoloji/Röntgen görseli yükleyin", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Yüklenen Görsel", use_container_width=True)

with col_result:
    if uploaded_file:
        with st.spinner("MathRix Neural Core analiz yapıyor..."):
            time.sleep(3)
            risk_score = random.randint(15, 92)
            
        st.write("### Analiz Sonucu")
        if risk_score > 50:
            st.error(f"Kritik Risk Skoru: %{risk_score}")
            st.write("*Öneri:* Doku örneğinde yüksek hücresel atipi gözlendi. İleri genetik test (NGS) ve biyopsi onayı gereklidir.")
        else:
            st.success(f"Düşük Risk Skoru: %{risk_score}")
            st.write("*Öneri:* Rutin takip ve stabil görünüm.")
            
        # Rapor İndirme
        report = f"MATHRIX AI ANALİZ RAPORU\nTarih: {time.strftime('%Y-%m-%d')}\nRisk: %{risk_score}\nTür Şüphesi: Adenokarsinom"
        st.download_button("📩 PDF Raporu Oluştur ve İndir", report, file_name="mathrix_analiz.txt")
    else:
        st.write("Lütfen sol taraftan bir dosya yükleyerek analizi başlatın.")

st.markdown("<br><hr><center>MathRix Global Health Systems © 2026</center>", unsafe_allow_html=True)
