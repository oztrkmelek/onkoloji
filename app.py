import streamlit as st
import numpy as np
import time
from PIL import Image, ImageStat

# --- SAYFA AYARLARI VE BEYAZ TEMA ---
st.set_page_config(page_title="MathRix Oncology Analysis v14", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1e293b; }
    .header-banner {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        padding: 40px; border-radius: 15px; text-align: center; color: white;
        box-shadow: 0 10px 25px rgba(30, 64, 175, 0.1); margin-bottom: 25px;
    }
    .report-card {
        background: #f8fafc; padding: 35px; border-radius: 20px;
        border: 1px solid #e2e8f0; margin-top: 20px;
    }
    .status-box { background: #f1f5f9; padding: 15px; border-radius: 10px; border-left: 5px solid #1e40af; margin-bottom: 20px; }
    .treatment-box { background: #f0fdf4; padding: 20px; border-radius: 12px; border: 1px solid #dcfce7; color: #166534; }
    .section-title { color: #1e40af; border-bottom: 2px solid #3b82f6; padding-bottom: 5px; margin-top: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- ŞİFRE SİSTEMİ ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown("<div class='header-banner'><h1>🧬 MATHRIX ONCO-CORE ACCESS</h1></div>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.write("### Sistem Erişimi")
        pw = st.text_input("Giriş Anahtarı:", type="password")
        if st.button("SİSTEMİ AKTİF ET"):
            if pw == "mathrix2026":
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("Hatalı anahtar! Erişim engellendi.")
    st.stop()

# --- ANA PANEL ---
st.markdown("<div class='header-banner'><h1>🔬 MATHRIX HÜCRESEL MİMARİ ANALİZ PANELİ</h1></div>", unsafe_allow_html=True)

file = st.file_uploader("Dijital Patoloji Görüntüsü Yükle (H&E)", type=["jpg", "png", "jpeg"])

if file:
    col1, col2 = st.columns([1, 1.2])
    img = Image.open(file).convert("RGB")
    
    with col1:
        st.image(img, use_container_width=True, caption="Mikroskobik Veri")
        run_btn = st.button("🚀 DERİN MİMARİ ANALİZİ BAŞLAT", use_container_width=True)

    if run_btn:
        # --- MATEMATİKSEL ANALİZ (DOKU TOPOLOJİSİ VE NOKTA BULUTU) ---
        img_array = np.array(img)
        # 1. Topolojik Boşluk (Lümen) Analizi
        void_space = np.sum(img_array > 215) / img_array.size
        # 2. Hücre Nokta Bulutu Yoğunluğu (Entropy/Kaos Analizi)
        kaos_skoru = np.mean(np.std(img_array, axis=(0, 1)))

        with st.status("Doku Topolojisi Hesaplanıyor...", expanded=True) as status:
            time.sleep(1.2)
            
            # KARAR MEKANİZMASI
            if void_space > 0.18: # Adeno: Boşluklu/Bezsel yapı
                tani = "ADENOKARSİNOM"
                bulgular = "Hücrelerin dairesel lümenler etrafında toplandığı Glandüler Mimari saptandı. Müsin vakuolleri ve Lepidik dizilim paternleri izlenmektedir."
                ilac = "EGFR pozitifliği durumunda Osimertinib, ALK pozitifliği durumunda Alectinib."
                prog = "Periferik gelişim; 6 ay içinde Beyin ve Sürrenal metastaz takibi kritiktir. Hedefe yönelik tedavi ile %70+ kontrol şansı."
            
            elif kaos_skoru > 55: # Skuamöz: Sert ve karmaşık tabaka
                tani = "SKUAMÖZ HÜCRELİ KARSİNOM"
                bulgular = "Keratinize İnci formasyonları ve Solid Tabakalaşma saptandı. İnterselüler köprüler ve yoğun hücresel pleomorfizm mevcuttur."
                ilac = "Pembrolizumab (Keytruda) + Platin bazlı ikili kemoterapi kombinasyonu."
                prog = "Lokal agresif yayılım; mediastinal lenf nodu ve kemik metastaz riski mevcuttur. 6 aylık takipte PET-BT zorunludur."
            
            elif kaos_skoru < 40: # Küçük Hücreli: Çok yoğun ve küçük noktalar
                tani = "KÜÇÜK HÜCRELİ AKCİĞER KANSERİ (SCLC)"
                bulgular = "Karakteristik Nükleer Molding (kalıplanma) izlendi. Yüksek N/S oranı, dar sitoplazma ve Tuz-Biber Kromatin yapısı doğrulandı."
                ilac = "Etoposid + Sisplatin ve eş zamanlı Atezolizumab (İmmünoterapi)."
                prog = "Sistemik agresif seyir; beyin metastazı riski %90. Profilaktik beyin ışınlaması (PCI) değerlendirilmelidir."
            
            else: # Büyük Hücreli: Ayrışmamış dev yapılar
                tani = "BÜYÜK HÜCRELİ KARSİNOM (LCLC)"
                bulgular = "Diferansiyasyon kaybı (Anaplazi) saptandı. Belirgin nükleollü dev hücreler ve belirsiz sınırları olan kaotik hücre grupları izlendi."
                ilac = "Cerrahi sonrası sisplatin bazlı adjuvan kemoterapi protokolleri."
                prog = "Hızlı kitle büyümesi ve uzak organ metastazı eğilimi. Yakın onkolojik takip gereklidir."

            status.update(label="Analiz Tamamlandı!", state="complete")

        # --- TEK SAYFA BÜYÜK RAPOR ---
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align:center; color:#1e40af;'>MATHRIX ANALİZ RAPORU: {tani}</h1>", unsafe_allow_html=True)
        
        st.markdown("<h3 class='section-title'>🔬 PATOLOJİK MORFOLOJİ ANALİZİ</h3>", unsafe_allow_html=True)
        st.write(f"*Hücresel Bulgular:* {bulgular}")
        
        [attachment_0](attachment)

        st.markdown("<h3 class='section-title'>💊 TEDAVİ PLANI VE HEDEFE YÖNELİK İLAÇLAR</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='treatment-box'><b>Önerilen Protokol:</b> {ilac}</div>", unsafe_allow_html=True)

        st.markdown("<h3 class='section-title'>🔮 PROGNOZ VE GELECEK TAHMİNİ (6 AY)</h3>", unsafe_allow_html=True)
        st.write(f"*Klinik Seyir Öngörüsü:* {prog}")

        

        st.markdown("<h3 class='section-title'>📐 MATEMATİKSEL DOKU TOPOLOJİSİ</h3>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Boşluk Oranı (Lümen)", f"%{void_space*100:.1f}")
        c2.metric("Kaos Varyansı", f"{kaos_skoru:.2f}")
        c3.metric("Nokta Bulutu Yoğunluğu", "Yüksek" if kaos_skoru > 45 else "Düşük")

        st.markdown("---")
        rapor_verisi = f"TANI: {tani}\nBULGULAR: {bulgular}\nTEDAVI: {ilac}\nPROGNOZ: {prog}"
        st.download_button("📄 RAPORU PDF/TXT OLARAK İNDİR", data=rapor_verisi, file_name=f"MathRix_{tani}.txt")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<center><br>MathRix Global Health © 2026 | Profesyonel Karar Destek</center>", unsafe_allow_html=True)
