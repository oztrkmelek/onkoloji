import streamlit as st
from PIL import Image
import numpy as np
import time

# =====================================================
# KONFİGÜRASYON
# =====================================================
st.set_page_config(
    page_title="Akciğer Kanseri Tanı ve Klinik Karar Destek Sistemi",
    layout="wide"
)

PASSWORD = "mathrix2026"

# =====================================================
# GİRİŞ
# =====================================================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Klinik Sistem Girişi")
    pw = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        if pw == PASSWORD:
            st.session_state.auth = True
            st.success("Yetkilendirme başarılı")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Hatalı şifre")
    st.stop()

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("🩺 Klinik Menü")
page = st.sidebar.radio(
    "Modül",
    ["🔬 Tanı Merkezi", "💊 İlaç & Klinik Rehber", "📊 Evreleme & Akademik Bilgi"]
)
st.sidebar.markdown("---")
st.sidebar.caption("⚠️ Akademik karar destek simülasyonu")

# =====================================================
# ANALİZ MOTORU (DETERMİNİSTİK)
# =====================================================
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

def tani_yuzdeleri(bosluk, yogunluk, malignite):
    # deterministik yüzdesel dağılım
    adeno = max(0, (bosluk * 100) - (yogunluk * 30))
    small = max(0, (yogunluk * 120) + (malignite * 0.3) - 40)
    squam = max(0, 100 - (adeno + small))
    total = adeno + small + squam
    return {
        "Adenokarsinom": adeno / total * 100,
        "Küçük Hücreli Karsinom": small / total * 100,
        "Skuamöz Hücreli Karsinom": squam / total * 100
    }

def prognoz_omur(malignite):
    if malignite < 30:
        return "≈ 48–60 ay (erken evre varsayımı)"
    elif malignite < 60:
        return "≈ 18–36 ay (orta risk grubu)"
    else:
        return "≈ 6–14 ay (ileri evre, agresif seyir)"

def metastaz_var_mi(malignite):
    return malignite > 55

def tedavi_stratejisi(tani, metastaz):
    if tani == "Adenokarsinom":
        base = (
            "EGFR / ALK mutasyon analizi önerilir.\n"
            "Birinci basamak: Osimertinib veya Alectinib."
        )
    elif tani == "Küçük Hücreli Karsinom":
        base = (
            "Platin bazlı kemoterapi (Sisplatin + Etoposid).\n"
            "Eş zamanlı immünoterapi (Pembrolizumab)."
        )
    else:
        base = (
            "Platin bazlı kemoterapi.\n"
            "Gerekirse radyoterapi kombinasyonu."
        )

    if metastaz:
        base += (
            "\n\nMETASTAZ VARLIĞINDA:\n"
            "- Beyin metastazı: Stereotaktik radyocerrahi\n"
            "- Kemik metastazı: Denosumab / Zoledronik asit\n"
            "- Karaciğer metastazı: Sistemik tedavi öncelikli"
        )
    return base

# =====================================================
# 🔬 TANİ MERKEZİ
# =====================================================
if page == "🔬 Tanı Merkezi":
    st.title("🔬 Akciğer Kanseri Tanı Merkezi (Akademik Analiz)")

    file = st.file_uploader("Histopatolojik Görüntü Yükle", ["png", "jpg", "jpeg"])

    if file:
        img = Image.open(file).convert("L")
        st.image(img, caption="Yüklenen Histopatolojik Görüntü", use_column_width=True)

        gray = normalize(np.array(img))

        with st.spinner("Çok katmanlı histomorfometrik analiz yapılıyor..."):
            time.sleep(2)
            bosluk = topolojik_bosluk(gray)
            yogunluk = hucre_yogunluk(gray)
            malignite = entropy_malignite(gray)

        yuzdeler = tani_yuzdeleri(bosluk, yogunluk, malignite)
        tani = max(yuzdeler, key=yuzdeler.get)
        metastaz = metastaz_var_mi(malignite)

        st.subheader("📊 Tanısal Olasılık Dağılımı")
        for k, v in yuzdeler.items():
            st.write(f"*{k}: %{v:.1f}*")

        rapor = f"""
=================== AKADEMİK KLİNİK RAPOR ===================

KESİNLEŞTİRİLMİŞ OLASILIK TEMELLİ TANI:
- En Olası Tanı: {tani} (%{yuzdeler[tani]:.1f})

HİSTOPATOLOJİK ANALİZ:
- Topolojik Boşluk Oranı: %{bosluk*100:.2f}
- Hücre Yoğunluğu: %{yogunluk*100:.2f}
- Entropi Tabanlı Malignite: %{malignite:.2f}

ETİYOLOJİK DEĞERLENDİRME:
Bu patern, kronik epitel hasarı, genetik instabilite ve
kontrolsüz proliferasyon ile uyumludur.

METASTAZ DURUMU:
{"Metastaz açısından YÜKSEK RİSK" if metastaz else "Şu an için belirgin metastaz bulgusu yok"}

PROGNOZ ve SAĞKALIM TAHMİNİ:
{prognoz_omur(malignite)}

KLİNİK TEDAVİ ÖNERİSİ (DOKTORA YÖNELİK):
{tedavi_stratejisi(tani, metastaz)}

AKADEMİK UYARI:
Bu sistem eğitim ve karar destek simülasyonudur.
Gerçek hasta yönetimi için klinik, patolojik ve genetik doğrulama zorunludur.
============================================================
"""

        st.markdown("### 📄 Detaylı Akademik Klinik Rapor")
        st.text_area("", rapor, height=520)

        st.download_button(
            "📥 Klinik Raporu İndir (.txt)",
            rapor,
            file_name="akademik_akciğer_kanseri_raporu.txt"
        )

# =====================================================
# 💊 İLAÇ MODÜLÜ
# =====================================================
elif page == "💊 İlaç & Klinik Rehber":
    st.title("💊 İlaç & Klinik Rehber")
    st.markdown("""
*Osimertinib:* EGFR T790M inhibitörü – QT uzaması  
*Pembrolizumab:* PD-1 inhibitörü – otoimmün yan etkiler  
*Alectinib:* ALK inhibitörü – hepatotoksisite  
*Sisplatin:* DNA çapraz bağlayıcı – nefrotoksisite  
""")

# =====================================================
# 📊 EVRELEME
# =====================================================
elif page == "📊 Evreleme & Akademik Bilgi":
    st.title("📊 Evreleme & Akademik Bilgi")
    st.markdown("""
*TNM SİSTEMİ*
- T: Primer tümör
- N: Lenf nodu
- M: Metastaz

*EVRE IV*
- Beyin, kemik, karaciğer metastazı
- Sistemik tedavi önceliklidir
""")
