import streamlit as st
from modules import image_processing, grading, clinical_guidelines, reporting, survival_prediction

st.set_page_config(page_title="MathRIX AI v5.0", layout="wide")

st.title("🧠 MathRIX AI v5.0")
st.write("Tıbbi Görüntü Analiz ve Prognostik Tahmin Sistemi")

# Sol panel - Görüntü yükleme
uploaded_file = st.file_uploader("📤 Görüntü Yükle (CT/MRI/PET)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Yüklenen Görüntü", use_column_width=True)

    if st.button("🔍 Analiz Başlat"):
        # Örnek özellik çıkarımı
        features = image_processing.extract_glcm_features(uploaded_file)
        grade_info = grading.calculate_grade(features)
        treatment = clinical_guidelines.get_treatment_protocol(grade_info["grade"], metastasis=False)
        survival = survival_prediction.predict_survival(grade_info["grade"])

        # Sonuçları göster
        st.subheader("📊 Analiz Sonuçları")
        st.write(f"**Derece:** Grade {grade_info['grade']} (Skor: {grade_info['score']})")
        st.write(f"**Tedavi Önerisi:** {treatment}")
        st.write(f"**Sağkalım Tahmini:** {survival}")

        # Rapor oluşturma
        if st.button("📄 Rapor Oluştur"):
            reporting.generate_report(uploaded_file, grade_info, treatment, survival)
            st.success("Rapor başarıyla oluşturuldu!")
