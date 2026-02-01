import streamlit as st
from PIL import Image
import numpy as np
import time

# =========================================================
# GENEL KONFİGÜRASYON
# =========================================================
st.set_page_config(
    page_title="Klinik Akciğer Kanseri Tanı & Karar Destek Sistemi",
    layout="wide"
)

PASSWORD = "mathrix2026"

# =========================================================
# GİRİŞ KONTROLÜ
# =========================================================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.markdown("## 🔐 Klinik Sistem Girişi")
    pwd = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş"):
        if pwd == PASSWORD:
            st.session_state.login = True
            st.success("Yetkilendirme başarılı")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Yetkisiz erişim")
    st.stop()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("🩺 Klinik Navigasyon")
page = st.sidebar.radio(
    "Modül Seç",
    [
        "🔬 Tanı Merkezi",
        "💊 İlaç & Farmakoloji",
        "📊 Evreleme & Klinik Veri"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("⚠️ Eğitim amaçlı karar destek simülasyonu")

# =========================================================
# GÖRÜNTÜ ANALİZ MOTORU (DETERMİNİSTİK)
# =========================================================
def normalize(img):
    img = img.astype(np.float32)
    return (img - img.min()) / (img.max() - img.min() + 1e-6)

def topolojik_bosluk(gray):
    return (gray < 0.35).mean()

def hucre_yogunluk(gray):
    return (gray > 0.60).mean()

def entropy_malignite(gray):
    hist, _ = np.histogram(gray.flatten(), bins=64, range=(0,1), density=True)
    hist = hist[hist > 0]
    entropy = -np.sum(hist * np.log2(hist))
    return min(100, (entropy / 6.0) * 100)

def tani_karari(bosluk, yogunluk, malignite):
    if bosluk > 0.45 and yogunluk < 0.30:
        return "Adenokarsinom", "Lepidik büyüme, glandüler boşluklar"
    elif yogunluk > 0.55 and malignite > 60:
        return "Küçük Hücreli Karsinom", "Azzopardi fenomeni, yoğun çekirdek kümelenmesi"
    else:
        return "Skuamöz Hücreli Karsinom", "Keratinize inci yapıları"

def prognoz(m):
    if m < 30:
        return "Düşük metastaz riski"
    elif m < 60:
        return "Orta risk – yakın takip"
    else:
        return "Yüksek risk – agresif seyir"

def metastaz_oneri(m):
    if m < 40:
        return "Şu an belirgin metastaz saptanmadı"
    return (
        "Beyin: Acil MR\n"
        "Kemik: PET / Sintigrafi\n"
        "Karaciğer: BT + LFT\n"
        "Onkoloji konsültasyonu önerilir"
    )

def tedavi(tani):
    if tani == "Adenokarsinom":
        return "Osimertinib (EGFR hedefli) – QT uzaması, döküntü"
    if tani == "Küçük Hücreli Karsinom":
        return "Sisplatin + Pembrolizumab – Nefrotoksisite, otoimmünite"
    return "Alectinib / Sisplatin – Hepatotoksisite, miyalji"

# =========================================================
# 🔬 TANİ MERKEZİ
# =========================================================
if page == "🔬 Tanı Merkezi":
    st.title("🔬 Tanı Merkezi")

    file = st.file_uploader("Histopatolojik Görüntü Yükle", ["png", "jpg", "jpeg"])

    if file:
        img = Image.open(file).convert("L")
        st.image(img, caption="Yüklenen Görüntü", use_column_width=True)

        img_np = normalize(np.array(img))

        with st.spinner("Deterministik klinik analiz çalışıyor..."):
            time.sleep(1.5)
            bosluk = topolojik_bosluk(img_np)
            yogunluk = hucre_yogunluk(img_np)
            malignite = entropy_malignite(img_np)

        tani, morfoloji = tani_karari(bosluk, yogunluk, malignite)

        rapor = f"""
================ KLİNİK AKCİĞER KANSERİ RAPORU ================

ŞU AN (TANI):
Olası Tanı: {tani}
Hücresel Morfoloji: {morfoloji}

ANALİTİK METRİKLER:
Topolojik Boşluk Oranı: %{bosluk*100:.2f}
Hücre Yoğunluğu: %{yogunluk*100:.2f}
Malignite Olasılığı: %{malignite:.2f}

GEÇMİŞ (ETİYOLOJİ):
Kronik hücresel hasar, genetik instabilite ve proliferatif düzensizlik.

GELECEK (PROGNOZ):
{prognoz(malignite)}

METASTAZ ANALİZİ:
{metastaz_oneri(malignite)}

TEDAVİ REHBERİ:
{tedavi(tani)}

UYARI:
Bu sistem klinik karar destek simülasyonudur.
Kesin tanı patolojik değerlendirme ile konur.
==============================================================
"""

        st.markdown("### 📄 Tek Sayfa Klinik Rapor")
        st.text_area("", rapor, height=420)

        st.download_button(
            "📥 Klinik Raporu İndir (.txt)",
            rapor,
            file_name="klinik_akciğer_kanseri_raporu.txt"
        )

# =========================================================
# 💊 İLAÇ & FARMAKOLOJİ
# =========================================================
elif page == "💊 İlaç & Farmakoloji":
    st.title("💊 İlaç & Farmakoloji")

    st.markdown("""
*Osimertinib*
- EGFR inhibitörü
- QT uzaması, döküntü

*Pembrolizumab*
- PD-1 immünoterapi
- Otoimmün komplikasyonlar

*Alectinib*
- ALK inhibitörü
- Hepatotoksisite

*Sisplatin*
- DNA çapraz bağlanması
- Nefrotoksisite
""")

# =========================================================
# 📊 EVRELEME
# =========================================================
elif page == "📊 Evreleme & Klinik Veri":
    st.title("📊 Evreleme & Klinik Veri")

    st.markdown("""
*TNM Sistemi*
- T: Tümör boyutu
- N: Lenf nodu
- M: Metastaz

*Evreler*
- Evre I: Lokal
- Evre II: Bölgesel
- Evre III: İleri lokal
- Evre IV: Uzak metastaz
""")
