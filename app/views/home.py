"""Home page for the irAE Clinical Safety Assistant."""

import streamlit as st
import os


def render():
    """Render the home page."""
    st.markdown(
        '<p class="main-header">🏥 irAE Clinical Safety Assistant</p>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="sub-header">AI-Powered Detection of Immune-Related Adverse Events in Oncology</p>',
        unsafe_allow_html=True
    )
    
    # Model Status Indicator
    _show_model_status()
    
    # Overview
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 What This Tool Does")
        st.markdown("""
        This clinical decision support system helps identify, classify, and triage 
        **immune-related adverse events (irAEs)** in patients receiving immunotherapy.
        
        **Key capabilities:**
        - 🔍 Parse clinical notes, labs, vitals, medications
        - 🎯 Detect organ-specific irAE patterns
        - 📊 CTCAE severity grading (Grade 1-4)
        - 🚨 Urgency triage classification
        - 📋 Structured clinical output
        """)
    
    with col2:
        st.markdown("### 🧬 Supported Organ Systems")
        st.markdown("""
        The system monitors for irAEs affecting:
        
        | System | Key Conditions |
        |--------|---------------|
        | 🫁 Pulmonary | Pneumonitis |
        | 🫀 Cardiac | Myocarditis |
        | 🧠 Neurologic | Neuropathy, Encephalitis |
        | 🦴 GI | Colitis, Diarrhea |
        | 🔬 Hepatic | Hepatitis |
        | ⚗️ Endocrine | Thyroiditis, Hypophysitis |
        | 🧴 Dermatologic | Rash, Dermatitis |
        """)
    
    st.markdown("---")
    
    # Quick start
    st.markdown("### 🚀 Quick Start")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **Step 1: Enter Patient Data**
        
        Input clinical notes, lab values, 
        medications, and symptoms.
        """)
    
    with col2:
        st.info("""
        **Step 2: Run Analysis**
        
        The system analyzes data for 
        irAE signals across all organ systems.
        """)
    
    with col3:
        st.info("""
        **Step 3: Review Results**
        
        Get structured findings with 
        severity grades and recommendations.
        """)
    
    # Start assessment button
    st.markdown("---")
    if st.button("📋 Start New Assessment", type="primary", use_container_width=True):
        st.session_state.current_page = "📋 New Assessment"
        st.rerun()
    
    # Important disclaimer
    st.markdown("---")
    st.markdown("""
    <div class="disclaimer-box">
    <strong>⚠️ Important Safety Information</strong><br><br>
    This tool is designed for <strong>clinical decision support only</strong>. It does not:
    <ul>
        <li>Replace clinical judgment or expertise</li>
        <li>Provide definitive diagnoses</li>
        <li>Prescribe medications or treatments</li>
    </ul>
    All findings should be <strong>verified by a qualified clinician</strong> before taking clinical action.
    </div>
    """, unsafe_allow_html=True)
    
    # Footer with immunotherapy context
    st.markdown("---")
    st.markdown("### 📚 Background: Immune Checkpoint Inhibitors")
    
    with st.expander("Learn about ICIs and irAEs"):
        st.markdown("""
        **Immune Checkpoint Inhibitors (ICIs)** are a class of cancer immunotherapy that work by 
        blocking inhibitory pathways, allowing the immune system to attack cancer cells.
        
        **Common ICI Classes:**
        - **PD-1 inhibitors:** Pembrolizumab (Keytruda), Nivolumab (Opdivo)
        - **PD-L1 inhibitors:** Atezolizumab (Tecentriq), Durvalumab (Imfinzi)
        - **CTLA-4 inhibitors:** Ipilimumab (Yervoy)
        
        **Immune-Related Adverse Events (irAEs)** occur when the activated immune system 
        attacks healthy tissues. These can affect virtually any organ system and range from 
        mild to life-threatening.
        
        **Key characteristics of irAEs:**
        - Can occur at any time during or after treatment
        - May affect multiple organ systems
        - Often subtle in early stages
        - Require prompt recognition and management
        - Most are reversible with appropriate treatment
        """)


def _show_model_status():
    """Show the AI model status indicator."""
    from src.llm.client import HuggingFaceClient
    
    llm_client = st.session_state.get("llm_client", None)
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        # Check if client exists and is HuggingFaceClient with model loaded
        if llm_client is not None and isinstance(llm_client, HuggingFaceClient):
            if llm_client.is_model_loaded():
                st.success("🤖 **MedGemma Active**")
            elif llm_client.get_loading_error():
                st.error("❌ **Model Error**")
                with st.expander("View Error"):
                    st.code(llm_client.get_loading_error())
            else:
                st.info("🔄 **Model Available**")
                st.caption("Model loads on first analysis")
        elif llm_client is not None:
            # Other LLM client (OpenAI, Anthropic)
            st.success("🤖 **LLM Active**")
        elif hf_token:
            st.info("🔄 **Ready to Load**")
            st.caption("Model loads on first analysis")
        else:
            st.warning("⚡ **Rule-Based Mode**")
            with st.expander("ℹ️ About Analysis Modes"):
                st.markdown("""
                **Current Mode: Rule-Based Analysis**
                
                The system is using deterministic clinical rules for irAE detection.
                This provides reliable pattern matching for:
                - Lab value abnormalities
                - Symptom pattern recognition
                - Medication identification
                - CTCAE grading
                
                **To enable AI-enhanced analysis:**
                1. Set `HF_TOKEN` environment variable
                2. Accept MedGemma terms at huggingface.co
                """)
