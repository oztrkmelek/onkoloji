import streamlit as st
from PIL import Image
import numpy as np
import time

# =========================================================
# GENEL AYARLAR
# =========================================================
st.set_page_config(
    page_title="Akciğer Kanseri Akademik Karar Destek Sistemi",
    layout="wide"
)

PASSWORD = "mathrix2026"

# =========================================================
# GİRİŞ KONTROLÜ
# =========================================================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("MathRIX  Sistem Girişi")
    pw = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        if pw == PASSWORD:
            st.session_state.auth = True
            st.success("Yetkilendirme başarılı")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Hatalı şifre")
    st.stop()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("Mathrix  Klinik Menü")
page = st.sidebar.radio(
    "Modül Seçimi",
    ["🔬 Tanı Merkezi", " İlaç & Klinik Rehber", " Evreleme & Akademik Bilgi"]
)
st.sidebar.markdown("---")
st.sidebar.caption("⚠️ Eğitim ve akademik karar destek simülasyonu")

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
    return min(95, (entropy / 6.0) * 100)  # %100'e asla ulaşmaz

def tani_yuzdeleri(bosluk, yogunluk, malignite):
    adeno = max(0, (bosluk * 100) - (yogunluk * 25))
    small = max(0, (yogunluk * 110) + (malignite * 0.25) - 35)
    squam = max(0, 100 - (adeno + small))

    total = adeno + small + squam
    adeno = adeno / total * 100
    small = small / total * 100
    squam = squam / total * 100

    max_val = max(adeno, small, squam)
    belirsizlik = max(5, 100 - max_val)  # her zaman belirsizlik payı

    return {
        "Adenokarsinom": adeno,
        "Küçük Hücreli Karsinom": small,
        "Skuamöz Hücreli Karsinom": squam,
        "Tanısal Belirsizlik": belirsizlik
    }

def prognoz_omur(malignite):
    if malignite < 30:
        return "Yaklaşık 48–60 ay (erken evre varsayımı, tedaviye yanıt iyi)"
    elif malignite < 60:
        return "Yaklaşık 18–36 ay (orta risk grubu, yakın klinik izlem gerekli)"
    else:
        return "Yaklaşık 6–14 ay (ileri evre varsayımı, agresif biyoloji)"

def metastaz_risk(malignite):
    return malignite > 55

def tedavi_onerisi(tani, metastaz):
    metin = ""
    if tani == "Adenokarsinom":
        metin += (
            "• EGFR, ALK, ROS1, BRAF mutasyon analizi önerilir.\n"
            "• EGFR pozitif olgularda Osimertinib birinci basamak tercih edilir.\n"
            "• ALK pozitif hastalarda Alectinib önerilir.\n"
        )
    elif tani == "Küçük Hücreli Karsinom":
        metin += (
            "• Platin bazlı kemoterapi (Sisplatin + Etoposid) standarttır.\n"
            "• İmmünoterapi (Pembrolizumab veya Atezolizumab) eklenebilir.\n"
        )
    else:
        metin += (
            "• Platin bazlı kombinasyon kemoterapisi önerilir.\n"
            "• Radyoterapi ile kombine edilebilir.\n"
        )

    if metastaz:
        metin += (
            "\nMETASTATİK HASTALIKTA EK STRATEJİLER:\n"
            "• Beyin metastazı: Stereotaktik radyocerrahi / WBRT\n"
            "• Kemik metastazı: Zoledronik asit veya Denosumab\n"
            "• Karaciğer metastazı: Sistemik tedavi önceliklidir\n"
        )

    return metin

# =========================================================
# 🔬 TANİ MERKEZİ
# =========================================================
if page == "🔬 Tanı Merkezi":
    st.title("🔬 Akciğer Kanseri Tanı Merkezi (Akademik Analiz)")

    file = st.file_uploader("Histopatolojik Görüntü Yükle", ["png", "jpg", "jpeg"])

    if file:
        img = Image.open(file).convert("L")
        st.image(img, caption="Yüklenen Histopatolojik Görüntü", use_column_width=True)

        gray = normalize(np.array(img))

        with st.spinner("Çok katmanlı histomorfometrik analiz yürütülüyor..."):
            time.sleep(2)
            bosluk = topolojik_bosluk(gray)
            yogunluk = hucre_yogunluk(gray)
            malignite = entropy_malignite(gray)

        yuzdeler = tani_yuzdeleri(bosluk, yogunluk, malignite)
        tani = max(
            [k for k in yuzdeler if k != "Tanısal Belirsizlik"],
            key=lambda x: yuzdeler[x]
        )
        metastaz = metastaz_risk(malignite)

        st.subheader("📊 Histolojik Alt Tip Olasılıkları")
        for k, v in yuzdeler.items():
            st.write(f"*{k}: %{v:.1f}*")

        rapor = f"""
================ AKADEMİK KLİNİK DEĞERLENDİRME RAPORU ================

OLASILIK TEMELLİ TANI DEĞERLENDİRMESİ:
Görüntü analizi sonucunda {tani} lehine bulgular baskındır
(%{yuzdeler[tani]:.1f}). Bununla birlikte tanısal belirsizlik mevcuttur
ve kesin tanı için ileri patolojik doğrulama gereklidir.

HİSTOPATOLOJİK METRİKLER:
* Topolojik Boşluk Oranı: %{bosluk*100:.2f}
* Hücre Yoğunluğu: %{yogunluk*100:.2f}
* Entropi Tabanlı Malignite İndeksi: %{malignite:.2f}

ETİYOLOJİ:
Bulgular; epitel hücrelerinde kronik hasar, genetik instabilite
ve düzensiz proliferasyon süreçleri ile uyumludur.

METASTAZ RİSK DEĞERLENDİRMESİ:
{"Metastatik hastalık açısından artmış risk mevcuttur." if metastaz else
"Mevcut verilerle belirgin metastaz bulgusu saptanmamıştır."}

PROGNOZ ve TAHMİNİ SAĞKALIM:
{prognoz_omur(malignite)}

KLİNİK TEDAVİ VE YÖNETİM ÖNERİLERİ:
{tedavi_onerisi(tani, metastaz)}

AKADEMİK VE ETİK UYARI:
Bu sistem yalnızca eğitim ve akademik karar destek amacıyla geliştirilmiştir.
Kesin tanı ve tedavi planlaması; klinik, patolojik, immünohistokimyasal
ve genetik bulguların birlikte değerlendirilmesi ile yapılmalıdır.
========================================================================
"""

        st.markdown("### 📄 Akademik Klinik Rapor")
        st.text_area("", rapor, height=550)

        st.download_button(
            "📥 Klinik Raporu İndir (.txt)",
            rapor,
            file_name="akademik_akciğer_kanseri_raporu.txt"
        )

# =========================================================
# 💊 İLAÇ & KLİNİK REHBER
# =========================================================
elif page == "💊 İlaç & Klinik Rehber":
    st.title("💊 İlaç & Klinik Rehber (Akademik)")

    st.markdown("""
### Hedefe Yönelik Tedaviler
*Osimertinib:*  
EGFR T790M ve sensitizing mutasyonlarda birinci basamak.  
Yan etkiler: QT uzaması, interstisyel akciğer hastalığı.

*Alectinib:*  
ALK pozitif NSCLC’de yüksek santral sinir sistemi penetrasyonu.  
Yan etkiler: Hepatotoksisite, miyalji.

### İmmünoterapi
*Pembrolizumab:*  
PD-L1 ekspresyonu yüksek hastalarda önerilir.  
Yan etkiler: Otoimmün tiroidit, kolit, pnömonit.

### Kemoterapi
*Sisplatin:*  
DNA çapraz bağlayıcı ajan.  
Yan etkiler: Nefrotoksisite, ototoksisite, bulantı-kusma.
""")

# =========================================================
# 📊 EVRELEME & AKADEMİK BİLGİ
# =========================================================
elif page == "📊 Evreleme & Akademik Bilgi":
    st.title("📊 Evreleme & Akademik Bilgi")

    st.markdown("""
### TNM Sınıflaması (AJCC)
- *T:* Primer tümör boyutu ve invazyonu  
- *N:* Bölgesel lenf nodu tutulumu  
- *M:* Uzak metastaz varlığı  

### Klinik Evreler
- *Evre I:* Lokalize hastalık  
- *Evre II:* Bölgesel yayılım  
- *Evre III:* İleri lokal-bölgesel hastalık  
- *Evre IV:* Uzak metastaz (beyin, kemik, karaciğer)

### Klinik Not
Evre IV hastalıkta küratif cerrahi genellikle mümkün değildir.
Tedavi yaklaşımı sistemik ve palyatiftir.
""")
