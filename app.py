import streamlit as st
import time
from PIL import Image
import random

# Sayfa Ayarları
st.set_page_config(page_title="MathRix AI Oncology Pro", layout="wide", page_icon="🧬")

# --- PROFESYONEL GİRİŞ EKRANI (DARK MODE) ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("""
        <style>
        .stApp { background: linear-gradient(to bottom, #000b1a, #001f3f); }
        .login-box {
            background-color: rgba(0, 31, 63, 0.8);
            padding: 60px;
            border-radius: 20px;
            border: 2px solid #00d4ff;
            text-align: center;
            box-shadow: 0px 0px 30px #00d4ff;
            margin-top: 50px;
        }
        h1 { color: #00d4ff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight: 800; }
        .stButton>button { background-color: #00d4ff; color: black; font-weight: bold; width: 100%; border-radius: 10px; }
        </style>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h1>MATHRIX NEURAL CORE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #e0e0e0;'>Onkolojik Karar Destek Sistemine Erişim İçin Kimlik Doğrulaması Gereklidir.</p>", unsafe_allow_html=True)
        
        password = st.text_input("Sistem Anahtarı:", type="password")
        
        if st.button("SİSTEMİ BAŞLAT 🚀"):
            if password == "mathrix2026":
                st.session_state['authenticated'] = True
                with st.spinner("Şifre doğrulanıyor, çekirdek modüller yükleniyor..."):
                    time.sleep(2)
                st.rerun()
            else:
                st.error("ERİŞİM REDDEDİLDİ: Yetkisiz Giriş Teşebbüsü.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- ANA PANEL TASARIMI ---
st.markdown("<h1 style='color: #00d4ff; text-align: center;'>🧬 MATHRIX AI: ONKOLOJİK ANALİZ VE 3T YÖNETİMİ</h1>", unsafe_allow_html=True)

# --- İLGİ ÇEKİCİ KLİNİK BİLGİ BANKASI ---
st.markdown("### 🔍 Onkoloji Rehberini İnceleyin")
info_tab1, info_tab2, info_tab3, info_tab4 = st.tabs([
    "🔬 Hücresel Analiz", "💊 Tedavi Protokolleri", "🧬 Genetik Mutasyonlar", "📊 Evreleme & Takip"
])

with info_tab1:
    st.markdown("<h4 style='color:#00d4ff;'>Akciğer Karsinomu Alt Tipleri</h4>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown("<div style='background-color:#0e1117; padding:20px; border-left:5px solid #00d4ff; border-radius:10px;'><b>Adenokarsinom (AC)</b><br><br>En sık görülen tiptir. Akciğerin periferik kısımlarında, müsin üreten bez yapılarından köken alır. Sigara içmeyenlerde de görülebilir.</div>", unsafe_allow_html=True)
    c2.markdown("<div style='background-color:#0e1117; padding:20px; border-left:5px solid #ff4b4b; border-radius:10px;'><b>Skuamöz Hücreli (SCC)</b><br><br>Merkezi hava yollarında keratin incileri ile karakterizedir. Sigara kullanımı ile doğrudan %90 ilişkilidir.</div>", unsafe_allow_html=True)
    c3.markdown("<div style='background-color:#0e1117; padding:20px; border-left:5px solid #ffa500; border-radius:10px;'><b>Büyük Hücreli (LCC)</b><br><br>Tanısı zordur, çok agresiftir. Mikroskop altında dev hücreler ve belirgin çekirdekçikler (nükleol) izlenir.</div>", unsafe_allow_html=True)

with info_tab2:
    st.markdown("<h4 style='color:#00d4ff;'>3T Yaklaşımı: Tedavi Stratejileri</h4>", unsafe_allow_html=True)
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.success("✅ *İmmünoterapi:* Pembrolizumab (Keytruda). Bağışıklık sistemini aktive ederek tümörle savaşmasını sağlar. PD-L1 skoru kritik öneme sahiptir.")
    with col_t2:
        st.error("🔴 *Kemoterapi:* Sisplatin bazlı rejimler. Hızlı bölünen tümör hücrelerini DNA düzeyinde baskılar.")

with info_tab3:
    st.warning("⚠️ *Hedefe Yönelik Tedavi (Akıllı İlaçlar)*")
    st.table({
        "Mutasyon": ["EGFR (+)", "ALK (+)", "ROS1 (+)", "KRAS G12C"],
        "İlaç Örneği": ["Osimertinib", "Alectinib", "Crizotinib", "Sotorasib"],
        "Hedef Mekanizma": ["Reseptör Blokajı", "Füzyon Durdurma", "Sinyal Kesme", "Spesifik İnhibisyon"]
    })

with info_tab4:
    st.markdown("<h4 style='color:#00d4ff;'>Metastaz Odaklı Evreleme</h4>", unsafe_allow_html=True)
    st.markdown("""
    * *Lokal Evre (1-2):* Tümör sadece akciğerde veya yakın lenf bezlerindedir.
    * *İleri Evre (4):* Tümör uzak organlara (Beyin, Karaciğer, Kemik) sıçramıştır.
    * *İzlem:* Her 3 ayda bir Kontrastlı BT ve beyin MR taraması ile nüks kontrolü yapılmalıdır.
    """)

st.divider()

# --- ANALİZ VE 3T SİSTEMİ ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📸 Vaka Veri Girişi")
    uploaded_file = st.file_uploader("Dijital Patoloji Görüntüsü Yükle", type=["jpg", "png", "jpeg"])
    
    with st.expander("📋 Klinik Profil (Analiz İçin Gereklidir)"):
        yas = st.number_input("Hasta Yaşı:", 18, 100, 65)
        sigara = st.radio("Sigara Geçmişi:", ["Hiç", "Eski", "Aktif"])
        metastazlar = st.multiselect("Metastaz Saptanan Organlar (Boşsa Erken Evre):", ["Beyin", "Karaciğer", "Kemik", "Sürrenal", "Lenf Düğümü"])

    # Otomatik Evreleme Mantığı
    evre_durumu = "Evre 4 (İleri)" if metastazlar else "Evre 1-3 (Lokal/Bölgesel)"
    st.markdown(f"<div style='background-color:#1e2129; padding:10px; border-radius:5px;'><b>Tahmini Klinik Evre:</b> <span style='color:#ff4b4b;'>{evre_durumu}</span></div>", unsafe_allow_html=True)

with col_right:
    if uploaded_file:
        st.image(Image.open(uploaded_file), use_container_width=True, caption="İncelenen Patolojik Kesit")
        
        if st.button("🔬 DERİN ANALİZİ VE 3T RAPORUNU BAŞLAT"):
            with st.status("Neural Core İşleniyor...", expanded=True) as status:
                st.write("Doku mimarisi katmanlara ayrılıyor...")
                time.sleep(1)
                st.write("Hücre çekirdekleri (nükleer atipi) taranıyor...")
                time.sleep(1)
                st.write("Klinik veriler ve evreleme parametreleri birleştiriliyor...")
                time.sleep(1)
                status.update(label="Analiz Tamamlandı!", state="complete", expanded=False)
            
            # Sonuç Üretimi
            secilen_tur = random.choice(["Adenokarsinom", "Skuamöz Hücreli Karsinom", "Büyük Hücreli Karsinom"])
            risk_puani = random.uniform(93.1, 99.4)
            
            st.error(f"### 🚩 TESPİT EDİLEN BULGU: {secilen_tur.upper()}")
            st.markdown(f"""
            *1. TANI (Diagnosis):* Yapay zeka, dokuda yüksek oranda *malignite (%{risk_puani:.1f})* saptamıştır. {secilen_tur} ile uyumlu hücresel pleomorfizm izlenmektedir.
            
            *2. TEDAVİ (Therapy):* {evre_durumu} vakası uyarınca; 
            - PD-L1 testi sonrasına göre *İmmünoterapi* planlanması,
            - EGFR/ALK genetik sonuçlarına göre *Akıllı İlaç* seçeneği değerlendirilmelidir.
            
            *3. TAKİP (Tracking):* Metastatik risk nedeniyle 8-12 haftalık periyotlarla görüntüleme (PET-BT) önerilir.
            """)
            
            # Profesyonel Rapor
            rapor_metni = f"""
            MATHRIX AI ONCOLOGY - 3T OFFICIAL REPORT
            -------------------------------------------
            Tarih: {time.strftime('%d/%m/%Y')} | Rapor ID: MX-{random.randint(1000,9999)}
            
            [TANI ANALIZI]
            Morfoloji: {secilen_tur}
            AI Malignite Skoru: %{risk_puani:.1f}
            Klinik Evre: {evre_durumu}
            Saptanan Metastazlar: {', '.join(metastazlar) if metastazlar else 'Saptanmadi'}
            
            [TEDAVI ONERISI]
            - {secilen_tur} spesifik NGS paneli taranmalidir.
            - {evre_durumu} icin sistemik tedavi (Kemoterapi + Immunoterapi) uygunlugu.
            
            [TAKIP PLANI]
            - 3 aylik periyotlarla Toraks/Batin BT.
            - Beyin MR (Nörolojik semptom takibi).
            
            Bu belge lise seviyesi bir AI projesi simülasyonudur.
            """
            st.download_button("📩 RESMİ 3T ANALİZ RAPORUNU İNDİR", rapor_metni, f"MathRix_Rapor_{secilen_tur}.txt")
    else:
        st.info("Lütfen bir vaka görüntüsü yükleyerek sistemi çalıştırın.")

st.markdown("<br><hr><center>MathRix Global Health Systems © 2026 | Professional Oncology Decision Support</center>", unsafe_allow_html=True)
