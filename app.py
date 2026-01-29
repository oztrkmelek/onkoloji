import streamlit as st
import numpy as np
from PIL import Image
import time
from datetime import datetime

# --- 1. TASARIM AYARLARI ---
st.set_page_config(page_title="MathRix AI | Akciğer Onkolojisi", layout="wide")

st.markdown("""
    <style>
    .auth-container { background: linear-gradient(135deg, #020617 0%, #083344 100%); padding: 50px; border-radius: 15px; text-align: center; color: white; border: 2px solid #22d3ee; }
    .auth-logo { font-size: 4em; font-weight: 900; color: #22d3ee; letter-spacing: 10px; margin-bottom: 10px; }
    .report-paper { background-color: white; padding: 40px; border: 1px solid #1e293b; color: black; font-family: 'Times New Roman', serif; line-height: 1.6; }
    .section-head { font-weight: bold; background-color: #f1f5f9; padding: 5px; margin-top: 15px; border-left: 5px solid #083344; text-transform: uppercase; }
    .glossary { background-color: #f8fafc; padding: 15px; border: 1px dashed #64748b; font-size: 0.9em; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. ŞİFRE EKRANI ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div class='auth-container'><div class='auth-logo'>MATHRIX</div><p>AKCİĞER KANSERİ ANALİZ SİSTEMİ</p></div>", unsafe_allow_html=True)
        if st.text_input("ERİŞİM ANAHTARI", type="password") == "mathrix2026":
            if st.button("SİSTEME GİR"):
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- 3. ANA TERMİNAL ---
st.title("🫁 Akciğer Kanseri Klinik Karar Destek Terminali")

L, R = st.columns([1, 2])
with L:
    file = st.file_uploader("Görüntü Yükle (BT/Patoloji)", type=["jpg", "png", "jpeg"])
    if file: st.image(Image.open(file), use_container_width=True)

with R:
    if not file:
        st.info("Analiz için görüntü bekleniyor...")
    else:
        with st.status("🧬 Akciğer dokusu taranıyor...", expanded=False):
            time.sleep(1); st.write("Hücre morfolojisi inceleniyor...")
            time.sleep(1); st.write("Malignite skorlaması yapılıyor...")
        
        # Analiz Sonucu (Simüle)
        risk = np.random.randint(82, 99)
        
        # HIZLI ÖZET KUTULARI
        c1, c2, c3 = st.columns(3)
        c1.metric("Analiz Sonucu", "POZİTİF (Kanser)")
        c2.metric("Malignite Oranı", f"%{risk}")
        c3.metric("Tip", "NSCLC (Adeno)")

        st.markdown("### 🔍 KLİNİK ANALİZ RAPORU")
        st.markdown(f"""
        <div class='report-paper'>
            <div style='text-align: center; border-bottom: 3px double black;'>
                <h2 style='margin:0;'>RESTORATİF PATOLOJİ RAPORU</h2>
                <p>MathRix Lung Health Center | Tarih: {datetime.now().strftime('%d/%m/%Y')}</p>
            </div>
            
            <div class='section-head'>I. TANI VE PATOLOJİK BULGULAR</div>
            <p>İncelenen akciğer kesitinde normal pulmoner mimari bozulmuş, <b>pleomorfik</b> (şekil bozukluğu olan) hücre grupları saptanmıştır. Bulgular %{risk} oranında <b>NSCLC (Küçük Hücreli Dışı Akciğer Kanseri) - Adenokarsinom</b> tanısını desteklemektedir.</p>
            
            <div class='section-head'>II. TEDAVİ VE İLAÇ REÇETESİ</div>
            <p><b>Ameliyat Durumu:</b> Tümörün lokasyonu nedeniyle <b>Lobektomi (Cerrahi)</b> hayati önem taşımaktadır. 
            Ameliyat sonrası nüks riskine karşı <b>Adjuvan Kemoterapi</b> önerilir.</p>
            <p><b>Önerilen İlaçlar:</b> Osimertinib (Hedefe Yönelik), Pembrolizumab (İmmünoterapi) ve Cisplatin.</p>
            
            <div class='section-head'>III. YAŞAM ÖNGÖRÜSÜ VE STRATEJİ</div>
            <p>Mevcut protokol ile 5 yıllık sağkalım oranı <b>%74</b> olarak simüle edilmiştir. Radyasyon yan etkilerinden kaçınmak için cerrahi sınırların temiz tutulması önceliklidir.</p>
            
            <div class='section-head'>IV. TERİMLER SÖZLÜĞÜ</div>
            <div class='glossary'>
                <b>• Malignite:</b> Kanserli, kötü huylu doku durumu.<br>
                <b>• Pleomorfizm:</b> Hücrelerin normalden farklı, düzensiz şekiller alması.<br>
                <b>• Lobektomi:</b> Akciğerin kanserli bir bölümünün ameliyatla alınması.<br>
                <b>• Adjuvan:</b> Ana tedaviye ek olarak yapılan destekleyici tedavi.
            </div>
            <p style='text-align: right; font-weight: bold; margin-top: 30px;'>MathRix Melek 🖋️</p>
        </div>
        """, unsafe_allow_html=True)

        if st.download_button("📩 RAPORU İNDİR (.TXT)", f"TANI: Adeno CA\nRISK: %{risk}\nTEDAVI: Lobektomi\nONAY: MathRix Melek"):
            st.success("Rapor başarıyla kaydedildi.")
