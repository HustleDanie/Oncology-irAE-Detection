"""About page with information about the irAE Clinical Safety Assistant."""

import streamlit as st


def render():
    """Render the about page."""
    st.markdown("## ℹ️ About the irAE Clinical Safety Assistant")
    
    st.markdown("""
    ### Overview
    
    The **irAE Clinical Safety Assistant** is an AI-powered clinical decision support 
    tool designed to help clinicians detect, classify, and triage immune-related 
    adverse events (irAEs) in oncology patients receiving immunotherapy.
    
    ### Purpose
    
    Immune checkpoint inhibitors (ICIs) have revolutionized cancer treatment, but they 
    can cause immune-related adverse events affecting virtually any organ system. 
    These irAEs are often:
    
    - **Subtle in early stages** - easily missed in routine assessment
    - **Scattered across data sources** - buried in notes, labs, vitals
    - **Time-critical** - early detection improves outcomes
    
    This tool aims to:
    
    1. 🔍 **Detect** possible irAE signals from clinical data
    2. 📊 **Classify** severity using CTCAE-style grading
    3. 🚨 **Triage** urgency for clinical response
    4. 📋 **Document** findings in structured format
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### How It Works
    
    The system uses a combination of:
    
    - **Rule-based analyzers** for each organ system (GI, liver, lung, etc.)
    - **Pattern recognition** for lab values, symptoms, and clinical notes
    - **Clinical reasoning** based on immunotherapy toxicity guidelines
    - **Optional AI enhancement** for complex clinical reasoning
    
    #### Analyzed Data Sources
    
    | Data Type | What We Look For |
    |-----------|------------------|
    | Labs | Liver enzymes, thyroid function, troponin, etc. |
    | Vitals | Hypoxia, hypotension, tachycardia |
    | Symptoms | Organ-specific symptom patterns |
    | Medications | Immunotherapy agents and timing |
    | Clinical Notes | irAE-related terms and findings |
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Supported Organ Systems
    
    The system monitors for irAEs in the following organ systems:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🫁 Pulmonary**
        - Pneumonitis
        - Interstitial lung disease
        
        **🫀 Cardiac**
        - Myocarditis
        - Pericarditis
        
        **🧠 Neurologic**
        - Neuropathy
        - Encephalitis
        - Myasthenia gravis
        - Guillain-Barré syndrome
        
        **🦴 Gastrointestinal**
        - Colitis
        - Enteritis
        """)
    
    with col2:
        st.markdown("""
        **🔬 Hepatic**
        - Hepatitis
        - Liver injury
        
        **⚗️ Endocrine**
        - Thyroiditis
        - Hypophysitis
        - Adrenal insufficiency
        
        **🧴 Dermatologic**
        - Rash
        - Dermatitis
        - Severe cutaneous reactions
        
        **🫘 Renal**
        - Nephritis
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Safety & Limitations
    
    #### ⚠️ Important Limitations
    
    - This tool is for **clinical decision support only**
    - It does **not** replace clinical judgment
    - It does **not** provide definitive diagnoses
    - It does **not** prescribe treatments
    - All findings require **verification by a qualified clinician**
    
    #### When This Tool May Not Be Reliable
    
    - Incomplete or inaccurate input data
    - Atypical presentations
    - Multiple concurrent conditions
    - Off-label immunotherapy use
    - Pediatric patients (limited validation)
    
    ### References
    
    This tool is informed by clinical guidelines including:
    
    - ASCO/NCCN Management Guidelines for irAEs
    - CTCAE (Common Terminology Criteria for Adverse Events)
    - ESMO Clinical Practice Guidelines
    - Published literature on immunotherapy toxicity
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Technical Information
    
    **Version:** 0.1.0
    
    **Technology Stack:**
    - Python 3.11+
    - Streamlit (Web interface)
    - Pydantic (Data validation)
    - OpenAI/Anthropic API (Optional AI enhancement)
    
    **Source Code:**
    Available for institutional review and customization.
    """)
    
    st.markdown("---")
    
    # Contact/feedback section
    st.markdown("""
    ### Feedback
    
    If you have suggestions for improving this tool or have identified issues,
    please contact the development team or submit feedback through your institution's
    clinical informatics department.
    """)
