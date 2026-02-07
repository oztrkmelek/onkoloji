
    # Institutional Report Export
    report_df = pd.DataFrame({
        "Physician": [st.session_state.doctor_name],
        "Patient ID": [pid],
        "AI Grade Prediction": [grade],
        "Pathologist Ground Truth": [gtruth],
        "Ensemble Score": [f"{m['Score']:.2f}"],
        "Metastasis Status": ["M1" if m1_check else "M0"],
        "Survival Forecast": [proto['OS']],
        "Clinical Protocol": [proto['Med']],
        "Physician Notes": [doc_notes]
    })

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, index=False, sheet_name='MathRIX_Audit_v6')
    
    st.sidebar.download_button(
        label="📥 Download Institutional Audit (Excel)",
        data=buffer.getvalue(),
        file_name=f"MathRIX_v6_Audit_{pid}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Upload a histology image to initiate v6.0 diagnostic logic.")
