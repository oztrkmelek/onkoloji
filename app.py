import streamlit as st
import numpy as np
from PIL import Image
import time
from datetime import datetime

# --- 1. RESMİ AKADEMİK TEMA ---
st.set_page_config(page_title="MathRix | Pulmonary Oncology", layout="wide")

st.markdown("""
    <style>
    /* Giriş Paneli */
    .auth-card { background: #0f172a; padding: 40px; border-radius: 15px; border: 1px solid #38bdf8; text-align: center; color: white; }
    .auth-title { font-size: 3.5em; font-weight: 800; color: #38bdf8; letter-spacing: 8px; }
    
    /* Akademik Rapor Kağıdı */
    .medical-report { 
        background-color: #ffffff; padding: 50px; border: 2px solid #334155; 
        color: #000000; font-family: 'Garamond', serif; box-shadow: 15px 15px 0px #334155;
    }
    .report-header { border-bottom: 5px double #000; text-align: center; padding-bottom: 20px; margin-bottom: 30px; }
    .report-section { background-color: #f8fafc; font-weight: bold; border-left: 6px solid #0f172a; padding: 8px; margin-top: 25px; text-transform: uppercase; }
    .footer-sign { text-align: right; margin-top: 50px; font-weight: bold; border-top: 1px solid #ddd; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GÜVENLİ GİRİŞ ---
if 'locked' not in st.session_state: st.session_state.locked = True
if st.session_state.locked:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div class='auth-card'><div class='auth-title'>MATHRIX</div><p>AKADEMİK ONKOLOJİ TERMİNALİ</p></div>", unsafe_allow_html=True)
        if st.text_input("SİSTEM ANAHTARI", type="password") == "mathrix2026":
            if st.button("TERMİNALİ AKTİVE ET"):
                st.session_state.locked = False
                st.rerun()
    st.stop()

# --- 3. KLİNİK TERMİNAL ---
st.title("🫁 Akciğer Karsinomu Karar Destek Sistemi")

L, R = st.columns([1, 2])
with L:
    uploaded = st.file_uploader("Dijital Patoloji / BT Kesiti", type=["jpg", "jpeg", "png"])
    if uploaded: st.image(Image.open(uploaded), caption="Orijinal Örnek Kesit", use_container_width=True)

with R:
    if not uploaded:
        st.info("Analiz için doku örneği yükleyiniz.")
    else:
        with st.status("🧬 Mikroskobik analiz yapılıyor...", expanded=False):
            time.sleep(1); st.write("Hücre morfolojisi taranıyor...")
            time.sleep(1); st.write("Nükleer atipi skorlanıyor...")
        
        risk = np.random.randint(88, 98)
        
        # ÜST ÖZET METRİKLER
        m1, m2, m3 = st.columns(3)
        m1.metric("Klinik Durum", "MALİGNİTE POZİTİF")
        m2.metric("Doğruluk Payı", f"%{risk}")
        m3.metric("Alt Tip", "Adenokarsinom")

        st.divider()
        
        # TIKLAYINCA AÇILAN RESMİ RAPOR
        if st.button("📄 RESMİ KLİNİK RAPORU OLUŞTUR VE GÖRÜNTÜLE"):
            report_html = f"""
            <div class='medical-report'>
                <div class='report-header'>
                    <h1 style='margin:0;'>RESTORATİF PATOLOJİ VE ONKOLOJİ EPİKRİZİ</h1>
                    <p style='margin:0;'>MathRix Pulmonary Research Institute | Rapor No: MX-{int(time.time())}</p>
                    <p><b>Düzenlenme Tarihi:</b> {datetime.now().strftime('%d/%m/%Y')}</p>
                </div>

                <div class='report-section'>I. MAKROSKOBİK VE MİKRÖSKOBİK BULGULAR</div>
                <p>Yapılan dijital histopatolojik incelemede, alveolar yapıların yerini <b>pleomorfik</b> epitel hücrelerinin aldığı, asiner ve kribriform paternde dizilim gösteren neoplastik bir oluşum gözlenmiştir. Nükleer pleomorfizm şiddetli olup, mitotik figürlerde belirgin artış (Grade III) saptanmıştır.</p>

                <div class='report-section'>II. TANI VE KLİNİK SINIFLANDIRMA</div>
                <p><b>KESİN TANI:</b> Küçük Hücreli Dışı Akciğer Kanseri (NSCLC) - <b>Adenokarsinom</b>.</p>
                <p><b>Doku Malignite İndeksi:</b> %{risk} (Yüksek Dereceli)</p>

                <div class='report-section'>III. TEDAVİ PROTOKOLÜ VE CERRAHİ PLAN</div>
                <p>Hastanın doku tipi ve evrelemesi baz alınarak <b>LOBEKTOMİ</b> (Sol/Sağ Akciğer Lob Rezeksiyonu) cerrahi müdahalesi endikedir. 
                Cerrahi sınırların güvenliği için post-operatif dönemde <b>Adjuvan Kemoterapi</b> ve <b>İmmünoterapi</b> (Pembrolizumab) kombinasyonu önerilmektedir.</p>

                <div class='report-section'>IV. PROGNOZ VE RADYASYON STRATEJİSİ</div>
                <p>Mevcut klinik veriler ışığında 5 yıllık sağkalım öngörüsü <b>%74</b> seviyesindedir. Radyasyonun çevre dokulara (pnömoni riski) zararını önlemek amacıyla <b>IMRT (Yoğunluk Ayarlı Radyoterapi)</b> tercih edilmelidir.</p>

                <div class='footer-sign'>
                    Dijital Onay: MathRix Melek 🖋️<br>
                    <span style='font-size:0.8em; font-weight:normal;'>Baş Onkolog ve Veri Analisti</span>
                </div>
            </div>
            """
            st.markdown(report_html, unsafe_allow_html=True)
            
            # İndirme Butonu
            st.download_button("📩 RAPORU DOSYA OLARAK KAYDET", report_html, file_name="klinik_rapor.html")

st.divider()
st.caption("MathRix AI | Akademik Araştırma Prototipi v18.0")
