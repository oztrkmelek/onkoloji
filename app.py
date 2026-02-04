import streamlit as st
import numpy as np
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import io
import base64

# Sayfa ayarları
st.set_page_config(
    page_title="Mathrix AI - Pathology System",
    page_icon="🏥",
    layout="wide"
)

# Oturum durumunu başlat
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

# Fuhrman Grading veritabanı
FUHRMAN_GRADING = {
    1: {
        "description": "Nuclei round, uniform, ~10μm diameter. Inconspicuous nucleoli.",
        "therapy": ["Active Surveillance", "Partial Nephrectomy"],
        "color": "🟢"
    },
    2: {
        "description": "Nuclei slightly irregular, ~15μm. Visible nucleoli at 400x.",
        "therapy": ["Partial Nephrectomy", "Radical Nephrectomy"],
        "color": "🟡"
    },
    3: {
        "description": "Nuclei obviously irregular, ~20μm. Prominent nucleoli at 100x.",
        "therapy": ["Sunitinib", "Pazopanib", "Targeted Therapy"],
        "color": "🟠"
    },
    4: {
        "description": "Nuclei pleomorphic, >25μm. Macronucleoli, bizarre shapes.",
        "therapy": ["Nivolumab", "Ipilimumab", "Cabozantinib"],
        "color": "🔴"
    }
}

def analyze_image(image_file):
    """Görüntüyü analiz et"""
    try:
        # Resmi aç
        image = Image.open(image_file)
        
        # NumPy array'e çevir
        img_array = np.array(image)
        
        # Boyutları al
        if len(img_array.shape) == 3:
            height, width, _ = img_array.shape
        else:
            height, width = img_array.shape
        
        # AI simülasyonu - gerçek değerler
        # Görüntüden özellik çıkar
        if len(img_array.shape) == 3:
            # Renkli resim
            gray_value = np.mean(img_array)
        else:
            # Gri tonlamalı resim
            gray_value = np.mean(img_array)
        
        # Grade hesapla (simülasyon)
        # Bu kısımda gerçek AI modelinizi kullanacaksınız
        if width < 500 or height < 500:
            # Küçük/kalitesiz resim
            grade = 2
            mean_diameter = 15.0
        else:
            # Kaliteli resim
            # Gerçek uygulamada burada OpenCV ile nükleer analiz yapılır
            brightness = gray_value / 255.0
            complexity = (width * height) / 1000000
            
            # Grade hesapla
            if brightness > 0.7 and complexity > 1.5:
                grade = 3
                mean_diameter = 20.0
            elif brightness > 0.5:
                grade = 2
                mean_diameter = 15.0
            else:
                grade = 1
                mean_diameter = 10.0
        
        # Sonuçları döndür
        return {
            "patient_id": os.path.splitext(image_file.name)[0][:20],
            "grade": grade,
            "mean_diameter": mean_diameter,
            "therapy": FUHRMAN_GRADING[grade]["therapy"],
            "description": FUHRMAN_GRADING[grade]["description"],
            "image": image,
            "filename": image_file.name,
            "image_size": f"{width}x{height}",
            "success": True
        }
        
    except Exception as e:
        return {
            "patient_id": image_file.name[:20],
            "grade": "Error",
            "mean_diameter": 0,
            "therapy": ["Analysis Failed"],
            "description": f"Error: {str(e)}",
            "filename": image_file.name,
            "success": False
        }

def create_visualization(analysis_data):
    """Görselleştirme oluştur"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Grade dağılımı
    grades = [1, 2, 3, 4]
    colors = ['green', 'yellow', 'orange', 'red']
    
    ax1.bar(grades, [10, 15, 20, 25], color=colors, alpha=0.6)
    ax1.axhline(y=analysis_data["mean_diameter"], color='blue', 
                linestyle='--', linewidth=2, 
                label=f'Detected: {analysis_data["mean_diameter"]}μm')
    ax1.set_xlabel('Fuhrman Grade')
    ax1.set_ylabel('Nuclear Diameter (μm)')
    ax1.set_title('Grade vs Nuclear Size')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Terapi önerileri
    therapy = analysis_data["therapy"]
    ax2.barh(range(len(therapy)), [1]*len(therapy), color='skyblue')
    ax2.set_yticks(range(len(therapy)))
    ax2.set_yticklabels(therapy)
    ax2.set_xlabel('Recommendation Priority')
    ax2.set_title('Therapy Recommendations')
    ax2.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    return fig

# Ana uygulama
def main():
    st.title("🏥 Mathrix AI - Medical Pathology Analysis")
    st.markdown("### AI-Powered Fuhrman Grading System")
    
    # Yan menü
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3067/3067256.png", width=100)
        st.markdown("### Clinical Settings")
        
        hospital = st.text_input("Hospital/Clinic", "City General Hospital")
        doctor = st.text_input("Clinician", "Dr. Alex Morgan")
        
        st.markdown("---")
        st.markdown("#### Analysis Mode")
        mode = st.selectbox("Select Mode", 
                           ["Standard", "Comprehensive", "Rapid"], 
                           index=0)
        
        st.markdown("---")
        st.markdown("#### Grading Reference")
        with st.expander("Click to view grading criteria"):
            for grade in range(1, 5):
                st.markdown(f"*Grade {grade}* {FUHRMAN_GRADING[grade]['color']}")
                st.caption(FUHRMAN_GRADING[grade]["description"])
                st.write(f"Therapy: {', '.join(FUHRMAN_GRADING[grade]['therapy'])}")
                st.write("---")
    
    # Ana içerik
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 Upload Pathology Images")
        
        # Dosya yükleme
        uploaded_files = st.file_uploader(
            "Drag and drop JPG/PNG images here",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            help="Upload multiple pathology slide images"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} image(s) ready for analysis")
            
            # İşleme butonu
            if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
                with st.spinner("Analyzing images..."):
                    results = []
                    
                    # Tüm dosyaları işle
                    for file in uploaded_files:
                        result = analyze_image(file)
                        results.append(result)
                    
                    st.session_state.processed_data = results
                    st.rerun()
    
    with col2:
        st.subheader("📊 Batch Status")
        if st.session_state.processed_data:
            total = len(st.session_state.processed_data)
            successful = len([r for r in st.session_state.processed_data if r.get("success", False)])
            
            st.metric("Total Files", total)
            st.metric("Successfully Analyzed", successful)
            
            if successful > 0:
                grades = [r["grade"] for r in st.session_state.processed_data 
                         if r.get("success", False) and isinstance(r["grade"], (int, float))]
                if grades:
                    avg_grade = np.mean(grades)
                    st.metric("Average Grade", f"{avg_grade:.1f}")
    
    # Sonuçları göster
    if st.session_state.processed_data:
        st.markdown("---")
        st.subheader("📈 Analysis Results")
        
        # Tablar
        tab1, tab2, tab3 = st.tabs(["🔬 Detailed View", "📋 Summary Table", "📥 Export"])
        
        with tab1:
            # Dosya navigasyonu
            if len(st.session_state.processed_data) > 1:
                col_nav1, col_nav2 = st.columns([3, 1])
                with col_nav1:
                    file_names = [f"{i+1}. {d['filename']}" 
                                 for i, d in enumerate(st.session_state.processed_data)]
                    selected = st.selectbox("Select file to view", 
                                           range(len(file_names)),
                                           format_func=lambda x: file_names[x],
                                           index=st.session_state.current_index)
                    st.session_state.current_index = selected
            
            current = st.session_state.processed_data[st.session_state.current_index]
            
            # İki sütunlu görünüm
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                if current.get("success", False) and "image" in current:
                    st.image(current["image"], 
                            caption=f"Pathology Image: {current['filename']}",
                            use_container_width=True)
                else:
                    st.warning("⚠️ Image not available for display")
            
            with col_right:
                # Hasta bilgileri
                st.markdown(f"### Patient: {current['patient_id']}")
                
                # Grade gösterimi
                grade = current["grade"]
                if isinstance(grade, (int, float)):
                    color = FUHRMAN_GRADING[grade]["color"]
                    st.markdown(f"## {color} Fuhrman Grade {grade}")
                    
                    # Metrikler
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        st.metric("Nuclear Diameter", f"{current['mean_diameter']} μm")
                    with col_m2:
                        st.metric("Image Size", current.get("image_size", "N/A"))
                    
                    # Terapi önerileri
                    st.markdown("#### 💊 Recommended Therapy")
                    for therapy in current["therapy"]:
                        st.success(f"• {therapy}")
                    
                    # Açıklama
                    st.markdown("#### 🔬 Morphological Description")
                    st.info(current["description"])
                    
                    # Görselleştirme
                    st.markdown("#### 📊 Analysis Visualization")
                    fig = create_visualization(current)
                    st.pyplot(fig)
                else:
                    st.error(f"❌ Analysis failed: {current.get('description', 'Unknown error')}")
        
        with tab2:
            # Özet tablosu
            summary_data = []
            for result in st.session_state.processed_data:
                if result.get("success", False):
                    summary_data.append({
                        "Patient ID": result["patient_id"],
                        "Grade": result["grade"],
                        "Diameter (μm)": result["mean_diameter"],
                        "Therapy": ", ".join(result["therapy"]),
                        "File": result["filename"]
                    })
            
            if summary_data:
                df = pd.DataFrame(summary_data)
                st.dataframe(df, use_container_width=True)
                
                # İstatistikler
                st.subheader("📊 Batch Statistics")
                col_s1, col_s2, col_s3 = st.columns(3)
                
                with col_s1:
                    grade_counts = df["Grade"].value_counts()
                    st.write("*Grade Distribution:*")
                    for grade, count in grade_counts.items():
                        st.write(f"Grade {grade}: {count} cases")
                
                with col_s2:
                    avg_dia = df["Diameter (μm)"].mean()
                    st.metric("Avg Diameter", f"{avg_dia:.1f} μm")
                
                with col_s3:
                    if not df.empty:
                        most_common = df["Grade"].mode()[0]
                        st.metric("Most Common", f"Grade {most_common}")
            else:
                st.warning("No successful analyses to display")
        
        with tab3:
            st.subheader("📥 Download Reports")
            
            # CSV export
            if st.session_state.processed_data:
                export_data = []
                for result in st.session_state.processed_data:
                    if result.get("success", False):
                        export_data.append({
                            "Patient_ID": result["patient_id"],
                            "Fuhrman_Grade": result["grade"],
                            "Mean_Nuclear_Diameter_μm": result["mean_diameter"],
                            "Recommended_Therapy": ", ".join(result["therapy"]),
                            "Morphology": result["description"],
                            "Filename": result["filename"],
                            "Analysis_Date": datetime.now().strftime("%Y-%m-%d"),
                            "Hospital": hospital,
                            "Clinician": doctor
                        })
                
                if export_data:
                    df_export = pd.DataFrame(export_data)
                    
                    # CSV butonu
                    csv = df_export.to_csv(index=False)
                    st.download_button(
                        label="📄 Download CSV Report",
                        data=csv,
                        file_name=f"Mathrix_AI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                    # Excel butonu
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df_export.to_excel(writer, index=False, sheet_name='Analysis')
                        
                        # Grading referansı ekle
                        grade_ref = pd.DataFrame([
                            {"Grade": g, 
                             "Description": FUHRMAN_GRADING[g]["description"][:50] + "...",
                             "Therapy": ", ".join(FUHRMAN_GRADING[g]["therapy"])}
                            for g in range(1, 5)
                        ])
                        grade_ref.to_excel(writer, index=False, sheet_name='Grading_Guide')
                    
                    excel_data = excel_buffer.getvalue()
                    
                    st.download_button(
                        label="📊 Download Excel Report",
                        data=excel_data,
                        file_name=f"Mathrix_AI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                    st.info("📋 Reports include patient data, analysis results, and grading guidelines")
                else:
                    st.warning("No data available for export")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.9em;'>
        <p>Mathrix AI v2.0 | Medical Analysis System | For research use only</p>
        <p>Always consult with a qualified pathologist for clinical decisions</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Uygulamayı çalıştır
if _name_ == "_main_":
    main()
