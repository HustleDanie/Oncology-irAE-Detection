"""
Streamlit Web Application for irAE Detection

Main entry point for the clinical safety assistant web interface.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import get_settings
from src.llm.client import OpenAIClient, AnthropicClient, HuggingFaceClient
from src.llm.assessment_engine import IRAEAssessmentEngine

# --- App State Initialization ---

def get_llm_client():
    """Initialize and return the appropriate LLM client based on settings."""
    settings = get_settings()
    if "llm_client" not in st.session_state:
        if settings.llm_provider == "openai" and settings.openai_api_key:
            st.session_state.llm_client = OpenAIClient(api_key=settings.openai_api_key, model=settings.openai_model)
        elif settings.llm_provider == "anthropic" and settings.anthropic_api_key:
            st.session_state.llm_client = AnthropicClient(api_key=settings.anthropic_api_key, model=settings.anthropic_model)
        elif settings.llm_provider == "huggingface":
            st.session_state.llm_client = HuggingFaceClient(
                model_name=settings.huggingface_model,
                use_quantization=settings.use_quantization
            )
        else:
            st.session_state.llm_client = None
    return st.session_state.llm_client

def get_assessment_engine():
    """Initialize and return the assessment engine."""
    if "assessment_engine" not in st.session_state:
        settings = get_settings()
        llm_client = get_llm_client()
        use_llm = st.session_state.get("use_llm_for_assessment", settings.default_use_llm)
        st.session_state.assessment_engine = IRAEAssessmentEngine(llm_client=llm_client, use_llm=use_llm)
    return st.session_state.assessment_engine

# Initialize session state variables
if "patient_data" not in st.session_state:
    st.session_state.patient_data = None
if "assessment_result" not in st.session_state:
    st.session_state.assessment_result = None

from app.views import home, assessment, results, about, sample_cases


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="irAE Clinical Safety Assistant",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .urgency-emergency {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 1rem;
        margin: 1rem 0;
    }
    .urgency-urgent {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 1rem;
        margin: 1rem 0;
    }
    .urgency-soon {
        background-color: #fffde7;
        border-left: 5px solid #ffeb3b;
        padding: 1rem;
        margin: 1rem 0;
    }
    .urgency-routine {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
        padding: 1rem;
        margin: 1rem 0;
    }
    .disclaimer-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🏥 irAE Assistant")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "📋 New Assessment", "🧪 Sample Cases", "📊 Results", "ℹ️ About"],
        index=0,
    )
    
    # Safety disclaimer in sidebar
    st.sidebar.markdown("---")
    st.sidebar.warning(
        "⚠️ **Clinical Decision Support Only**\n\n"
        "This tool does not replace clinical judgment. "
        "All findings must be verified by a qualified clinician."
    )
    
    # Route to appropriate page
    if page == "🏠 Home":
        home.render()
    elif page == "📋 New Assessment":
        assessment.render()
    elif page == "🧪 Sample Cases":
        sample_cases.render()
    elif page == "📊 Results":
        results.render()
    elif page == "ℹ️ About":
        about.render()


# Call main() when the module is loaded by Streamlit
main()
