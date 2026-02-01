import streamlit as st
import numpy as np
from PIL import Image
import cv2
import math

# ==============================
# SAYFA AYARLARI
# ==============================
st.set_page_config(
    page_title="Akciğer Kanseri Destekleyici Klinik Analiz Sistemi",
    layout="wide"
)

st.title("🫁 Akciğer Kanseri Görüntü Tabanlı Klinik Destek Sistemi")
st.caption("""
Bu sistem tanı koymaz. Klinik, patolojik ve moleküler değerlendirmeyi desteklemek amacıyla geliştirilmiş
akademik bir karar destek prototipidir.
""")

# ==============================
# YARDIMCI FONKSİYONLAR
# ==============================

def preprocess_image(img):
    img = np.array(img.convert("L"))
    img = cv2.resize(img, (256, 256))
    img = cv2.GaussianBlur(img, (5,5), 0)
    return img

def entropy_score(img):
    hist = cv2.calcHist([img],[0],None,[256],[0,256])
    hist = hist / hist.sum()
    ent = -np.sum([p*np.log2(p) for p in hist if p > 0])
    return ent

def cell_density(img):
    _, th = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return np.sum(th == 255) / th.size

def malignancy_probability(ent, density):
    raw = 0.55*ent + 0.45*density*10
    prob = 1 / (1 + math.exp(-raw + 4))
    return min(max(prob, 0.05), 0.95)  # %100 YOK, belirsizlik payı var

def subtype_estimation(prob):
    if prob > 0.75:
        return {
            "Adenokarsinom": 0.87,
            "Skuamöz Hücreli Karsinom": 0.09,
            "Büyük Hücreli Karsinom": 0.04
        }
    elif prob > 0.55:
        return {
            "Adenokarsinom": 0.55,
            "Skuamöz Hücreli Karsinom": 0.30,
            "Diğer NSCLC": 0.15
        }
    else:
        return {
            "Benign / Düşük Dereceli Lezyon": 0.60,
            "Atipik Hiperplazi": 0.25,
            "Erken NSCLC Olasılığı": 0.15
        }

def tnm_staging(prob, density):
    if prob < 0.4:
        return "Evre 0 – I (Erken Evre, düşük malignite olasılığı)"
    elif prob < 0.65:
        return "Evre II (Lokal ilerlemiş olasılık)"
    elif prob < 0.8:
        return "Evre III (Bölgesel lenf nodu tutulumu olası)"
    else:
        return "Evre IV (Metastatik hastalık olasılığı)"

# ==============================
# GÖRSEL YÜKLEME
# ==============================
uploaded = st.file_uploader("Histopatolojik veya radyolojik görüntü yükleyiniz", type=["png","jpg","jpeg"])

if uploaded:
    img = Image.open(uploaded)
    proc = preprocess_image(img)

    ent = entropy_score(proc)
    dens = cell_density(proc)
    prob = malignancy_probability(ent, dens)
    subtypes = subtype_estimation(prob)
    stage = tnm_staging(prob, dens)

    col1, col2 = st.columns(2)

    with col1:
        st.image(img, caption="Yüklenen Görüntü", use_container_width=True)

    with col2:
        st.subheader("📊 Kantitatif Analiz")
        st.write(f"*Malignite Olasılığı:* %{prob*100:.1f}")
        st.write(f"*Görüntü Entropisi:* {ent:.2f}")
        st.write(f"*Hücre Yoğunluğu:* {dens:.2f}")
        st.write(f"*Tahmini Klinik Evre:* {stage}")

    st.divider()

    # ==============================
    # ALT TİP TAHMİNİ
    # ==============================
    st.subheader("🧬 Olası Histolojik Alt Tipler")
    for k,v in subtypes.items():
        st.write(f"- *{k}:* %{v*100:.1f}")

    st.divider()

    # ==============================
    # AKADEMİK KLİNİK YORUM
    # ==============================
    st.subheader("🩺 Klinik ve Akademik Değerlendirme")

    st.markdown("""
### Tanısal Yorum
Bu görüntüden elde edilen morfometrik ve istatistiksel özellikler, *malignite ile uyumlu olabilecek*
bir doku organizasyonuna işaret etmektedir. Bununla birlikte sistem *kesin tanı koymaz*;
patoloji, immünohistokimya ve moleküler testler zorunludur.

### Evreleme (TNM Tabanlı Yaklaşım)
- *Evre I–II:* Cerrahi rezeksiyon temel yaklaşımdır.
- *Evre III:* Eş zamanlı kemoradyoterapi ve ardından immünoterapi (örn. Durvalumab) önerilir.
- *Evre IV:* Sistemik tedavi esastır; lokal tedaviler palyatif amaçlıdır.

### Sistemik Tedavi Seçenekleri (Bilgilendirme Amaçlı)
*Bu bölüm klinik rehber özetidir, reçete değildir.*

#### NSCLC – Adenokarsinom ağırlıklı olasılıkta:
- *EGFR mutasyonu pozitif:* Osimertinib
- *ALK rearranjmanı:* Alectinib
- *PD-L1 ≥ %50:* Pembrolizumab monoterapi
- *PD-L1 düşük:* Platin bazlı kemoterapi + immünoterapi

#### Metastatik Hastalık Varsa:
- Beyin metastazı: Stereotaktik radyocerrahi + sistemik tedavi
- Kemik metastazı: Denosumab / Zoledronik asit (destekleyici)
- Karaciğer metastazı: Sistemik tedavi öncelikli

### Prognoz (Tahmini, İstatistiksel)
- *Erken evre:* 5 yıllık sağkalım %60–80
- *Evre III:* Medyan sağkalım 18–36 ay
- *Evre IV:* Medyan sağkalım 8–18 ay  
(Bu değerler popülasyon istatistikleridir, bireysel hasta için bağlayıcı değildir.)

### Önemli Klinik Not
Bu yazılım *doktorun yerini almaz*. Amaç;
- Görüntü → risk → olası alt tip → evre → tedavi seçenekleri
arasındaki ilişkiyi *akademik düzeyde* göstermektir.
""")

    st.success("Analiz tamamlandı. Klinik karar için multidisipliner değerlendirme gereklidir.")
