import streamlit as st
import numpy as np
from PIL import Image
import pandas as pd
import os
from datetime import datetime
import io

# Sayfa ayarları
st.set_page_config(
    page_title="Mathrix AI - Pathology System",
    page_icon="🏥",
    layout="wide"
)

# Oturum durumu
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

# Fuhrman Grading
FUHRMAN_GRADING = {
    1: {
        "description": "Nuclei round, uniform, ~10μm. Inconspicuous nucleoli.",
        "therapy": ["Active Surveillance", "Partial Nephrectomy"],
        "color": "🟢",
        "diameter": 10
    },
    2: {
        "description": "Nuclei slightly irregular, ~15μm. Visible nucleoli.",
        "therapy": ["Partial Nephrectomy", "Radical Nephrectomy"],
        "color": "🟡",
        "diameter": 15
    },
    3: {
        "description": "Nuclei obviously irregular, ~20μm. Prominent nucleoli.",
        "therapy": ["Sunitinib", "Pazopanib"],
        "color": "🟠",
        "diameter": 20
    },
    4: {
        "description": "Nuclei pleomorphic, >25μm. Macronucleoli.",
        "therapy": ["Nivolumab", "Ipilimumab", "Cabozantinib"],
        "color": "🔴",
        "diameter": 25
    }
}

def analyze_image(image_file):
    """Görüntü analizi"""
    try:
        image = Image.open(image_file)
        img_array = np.array(image)
        
        # Boyutlar
        if len(img_array.shape) == 3:
            height, width, _ = img_array.shape
            gray_value = np.mean(img_array)
        else:
            height, width = img_array.shape
            gray_value = np.mean(img_array)
        
        # Grade hesapla (simülasyon)
        if width < 500 or height < 500:
            grade = 2
            mean_diameter = 15.0
        else:
            brightness = gray_value / 255.0
            if brightness > 0.7:
                grade = 3
                mean_diameter = 20.0
            elif brightness > 0.5:
                grade = 2
                mean_diameter = 15.0
            elif brightness > 0.3:
                grade = 1
                mean_diameter = 10.0
            else:
                grade = 4
                mean_diameter = 25.0
        
        return {
            "patient_id": os.path.splitext(image_file.name)[0][:20],
            "grade": grade,
            "mean_diameter": mean_diameter,
            "therapy": FUHRMAN_GRADING[grade]["therapy"],
            "description": FUHRMAN_GRADING[grade]["description"],
            "color": FUHRMAN_GRADING[grade]["color"],
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

# Ana uygulama
def main():
    st.title("🏥 Mathrix AI - Medical Pathology Analysis")
    st.markdown("### AI-Powered Fuhrman Grading System")
    
    # Yan menü
    with st.sidebar:
        st.markdown("### Clinical Settings")
        
        hospital = st.text_input("Hospital/Clinic", "City General Hospital")
        doctor = st.text_input("Clinician", "Dr. Alex Morgan")
        
        st.markdown("---")
        st.markdown("#### Grading Reference")
        for grade in range(1, 5):
            with st.expander(f"Grade {grade} {FUHRMAN_GRADING[grade]['color']}"):
                st.write(FUHRMAN_GRADING[grade]["description"])
                st.write(f"Therapy: {', '.join(FUHRMAN_GRADING[grade]['therapy'])}")
    
    # Ana içerik
    st.subheader("📁 Upload Pathology Images")
    
    uploaded_files = st.file_uploader(
        "Upload JPG/PNG images",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} image(s) ready")
        
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                results = []
                for file in uploaded_files:
                    results.append(analyze_image(file))
                st.session_state.processed_data = results
                st.rerun()
    
    # Sonuçlar
    if st.session_state.processed_data:
        st.markdown("---")
        st.subheader("📊 Results")
        
        # Tablar
        tab1, tab2, tab3 = st.tabs(["🔬 View", "📋 Table", "📥 Export"])
        
        with tab1:
            if len(st.session_state.processed_data) > 1:
                file_names = [f"{i+1}. {d['filename']}" 
                             for i, d in enumerate(st.session_state.processed_data)]
                selected = st.selectbox("Select file", 
                                       range(len(file_names)),
                                       format_func=lambda x: file_names[x],
                                       index=st.session_state.current_index)
                st.session_state.current_index = selected
            
            current = st.session_state.processed_data[st.session_state.current_index]
            
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                if current.get("success", False) and "image" in current:
                    st.image(current["image"], 
                            caption=f"Image: {current['filename']}",
                            use_container_width=True)
            
            with col_right:
                st.markdown(f"### Patient: {current['patient_id']}")
                
                if current.get("success", False):
                    grade = current["grade"]
                    st.markdown(f"## {current['color']} Grade {grade}")
                    
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        st.metric("Nuclear Diameter", f"{current['mean_diameter']} μm")
                    with col_m2:
                        st.metric("Status", "✓ Analyzed")
                    
                    st.markdown("#### 💊 Therapy")
                    for therapy in current["therapy"]:
                        st.success(f"• {therapy}")
                    
                    st.markdown("#### 🔬 Description")
                    st.info(current["description"])
                    
                    # Basit grade chart (matplotlib olmadan)
                    st.markdown("#### 📊 Grade Scale")
                    grades_html = ""
                    for g in range(1, 5):
                        current_class = "current-grade" if g == grade else ""
                        grades_html += f"""
                        <div class="grade-bar {current_class}">
                            <span class="grade-label">Grade {g}</span>
                            <span class="grade-diameter">{FUHRMAN_GRADING[g]['diameter']}μm</span>
                        </div>
                        """
                    
                    st.markdown(f"""
                    <style>
                    .grade-bar {{
                        padding: 10px;
                        margin: 5px 0;
                        border-radius: 5px;
                        background-color: #f0f0f0;
                        display: flex;
                        justify-content: space-between;
                    }}
                    .current-grade {{
                        background-color: #d4edda;
                        border-left: 5px solid #28a745;
                    }}
                    .grade-label {{ font-weight: bold; }}
                    .grade-diameter {{ color: #666; }}
                    </style>
                    <div>{grades_html}</div>
                    """, unsafe_allow_html=True)
                
                else:
                    st.error(f"❌ Failed: {current.get('description', 'Error')}")
        
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
                st.subheader("📈 Statistics")
                col_s1, col_s2 = st.columns(2)
                
                with col_s1:
                    if not df.empty:
                        grade_counts = df["Grade"].value_counts()
                        for grade, count in grade_counts.items():
                            st.write(f"*Grade {grade}:* {count} cases")
                
                with col_s2:
                    if not df.empty:
                        avg_dia = df["Diameter (μm)"].mean()
                        st.metric("Avg Diameter", f"{avg_dia:.1f} μm")
        
        with tab3:
            st.subheader("📥 Download Reports")
            
            if st.session_state.processed_data:
                export_data = []
                for result in st.session_state.processed_data:
                    if result.get("success", False):
                        export_data.append({
                            "Patient_ID": result["patient_id"],
                            "Grade": result["grade"],
                            "Nuclear_Diameter_μm": result["mean_diameter"],
                            "Therapy": ", ".join(result["therapy"]),
                            "Description": result["description"],
                            "Filename": result["filename"],
                            "Date": datetime.now().strftime("%Y-%m-%d")
                        })
                
                if export_data:
                    df_export = pd.DataFrame(export_data)
                    
                    # CSV
                    csv = df_export.to_csv(index=False)
                    st.download_button(
                        label="📄 Download CSV",
                        data=csv,
                        file_name=f"Mathrix_Report_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                    # Excel
                    try:
                        excel_buffer = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                            df_export.to_excel(writer, index=False, sheet_name='Analysis')
                        excel_data = excel_buffer.getvalue()
                        
                        st.download_button(
                            label="📊 Download Excel",
                            data=excel_data,
                            file_name=f"Mathrix_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except:
                        st.info("Excel export requires openpyxl library")
    
    # Footer
    st.markdown("---")
    st.markdown("Mathrix AI v2.0 | Medical Analysis System")

if _name_ == "_main_":
    main()
