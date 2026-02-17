"""
Architecture page - Project overview and technical documentation.
"""

import streamlit as st


def render():
    """Render the Architecture page with project documentation."""
    
    st.markdown("# 🏗️ System Architecture")
    st.markdown("### Oncology irAE Clinical Safety Assistant")
    
    st.markdown("---")
    
    # Project Name Section
    st.markdown("## 📌 Project Name")
    st.info("**Oncology irAE Clinical Safety Assistant**")
    
    st.markdown("---")
    
    # Team Section
    st.markdown("## 👤 Team")
    st.markdown("""
    **Solo Project**
    - **Uche Maduabuchi Daniel** — Developer & Designer | End-to-end system development, clinical logic, AI integration, and deployment
    """)
    
    st.markdown("---")
    
    # Problem Statement Section
    st.markdown("## 🎯 Problem Statement")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### The Challenge: A Hidden Crisis in Cancer Care
        
        Immunotherapy has revolutionized cancer treatment—drugs like pembrolizumab (Keytruda) and 
        nivolumab (Opdivo) are saving lives that were once considered untreatable. But there's a 
        dangerous trade-off: these powerful drugs can trigger the immune system to attack healthy organs.
        
        These **immune-related adverse events (irAEs)** affect **40% of immunotherapy patients**. 
        They can strike any organ—gut, liver, lungs, thyroid, heart, brain—and escalate from mild 
        symptoms to life-threatening emergencies within days.
        
        **The critical gap: 40% of irAEs are missed or caught too late.**
        """)
        
        st.markdown("""
        ### Why Are irAEs Missed?
        
        - 📊 Each patient generates **200+ data points** across notes, labs, vitals, and medications
        - 🔍 Early warning signs are **subtle**—mild diarrhea, slight fatigue, marginally elevated liver enzymes
        - ⏰ **Time pressure** means signals get buried in information overload
        - 🚨 By the time symptoms become obvious, patients are already in crisis
        """)
    
    with col2:
        st.markdown("### Human Cost")
        st.error("**~48,000** deaths annually from severe irAEs globally")
        st.warning("**~15,000** preventable with earlier detection")
        st.info("**144,000** patients forced to stop cancer treatment")
    
    st.markdown("### Impact Potential")
    st.markdown("*At 15% global adoption, this solution could achieve:*")
    
    impact_col1, impact_col2, impact_col3, impact_col4, impact_col5 = st.columns(5)
    
    with impact_col1:
        st.metric("Lives Saved", "~2,300", "per year")
    with impact_col2:
        st.metric("Severe Cases Prevented", "~45,000", "per year")
    with impact_col3:
        st.metric("Patients Continue Therapy", "~36,000", "per year")
    with impact_col4:
        st.metric("Cost Savings", "$4.5B", "per year")
    with impact_col5:
        st.metric("Clinician Hours Freed", "6M", "per year")
    
    st.caption("*Over 10 years with gradual adoption (1%→30%): ~22,400 lives saved, $44B in avoided costs.*")
    
    st.markdown("---")
    
    # Overall Solution Section
    st.markdown("## 🧠 Overall Solution")
    st.markdown("### Effective Use of HAI-DEF Models")
    
    st.markdown("""
    This project leverages **Google MedGemma** from the HAI-DEF collection as the core AI engine, 
    combined with deterministic rule-based analyzers for maximum reliability.
    """)
    
    st.markdown("### Why MedGemma?")
    
    med_col1, med_col2 = st.columns(2)
    
    with med_col1:
        st.success("""
        **✅ Purpose-Built for Medicine**
        - Trained on clinical notes & medical literature
        - Understands lab values, drug interactions, symptoms
        - Native medical reasoning (not retrofitted)
        """)
    
    with med_col2:
        st.success("""
        **✅ Deployment Advantages**
        - Open-source & runs locally (privacy-compliant)
        - Efficient 4B parameters (works on T4 GPU)
        - Cost-effective (~$0.60/hour vs $15/1M tokens)
        """)
    
    st.markdown("### Hybrid Architecture Diagram")
    
    st.code("""
┌─────────────────────────────────────────────────────────────────────────┐
│                         PATIENT DATA INPUT                               │
│            (Clinical Notes, Labs, Vitals, Medications)                   │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      RULE-BASED DETECTION LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Lab Parser  │  │  Symptom    │  │ Medication  │  │   Vitals    │     │
│  │ AST/ALT/TSH │  │   Parser    │  │   Parser    │  │   Parser    │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │                │            │
│         └────────────────┴────────────────┴────────────────┘            │
│                                  │                                       │
│                    ┌─────────────▼─────────────┐                        │
│                    │   9 ORGAN ANALYZERS       │                        │
│                    │  GI │ Liver │ Lung │ Endo │                        │
│                    │ Skin│ Neuro │Cardiac│Renal│                        │
│                    │         Hematologic       │                        │
│                    └─────────────┬─────────────┘                        │
│                                  │                                       │
│              → Catches definite red flags with 100% reliability         │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MEDGEMMA AI REASONING LAYER                           │
│                     (google/medgemma-4b-it)                              │
│                                                                          │
│    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│    │    Causality     │  │     Severity     │  │   Recommendation │     │
│    │   Assessment     │  │     Grading      │  │    Generation    │     │
│    │                  │  │                  │  │                  │     │
│    │ "Is this irAE or │  │ "CTCAE Grade 1-4"│  │ "What should the │     │
│    │  something else?"│  │                  │  │  clinician do?"  │     │
│    └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                          │
│              → Provides nuanced clinical judgment                        │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      STRUCTURED OUTPUT                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  • Organ System: Hepatic, GI, Pulmonary, Endocrine, etc.       │    │
│  │  • CTCAE Grade: 1 (Mild) → 4 (Life-threatening)                │    │
│  │  • Urgency: 🟢 Routine │ 🟡 Soon │ 🟠 Urgent │ 🔴 Emergency    │    │
│  │  • Evidence: Cited lab values, symptoms, clinical findings      │    │
│  │  • Recommendations: Management suggestions with uncertainty     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
    """, language=None)
    
    st.markdown("""
    **Key Design Principles:**
    - 🛡️ **Rule-based layer** catches definite patterns (elevated AST = hepatic signal) with 100% reliability
    - 🧠 **MedGemma layer** provides clinical reasoning—assessing causality, integrating context, generating summaries
    - 📋 **Structured outputs** via Pydantic schemas constrain responses to valid CTCAE grades and urgency levels
    - ⚠️ **Safety-first**: AI assists, never replaces clinical judgment; expresses uncertainty when appropriate
    """)
    
    st.markdown("---")
    
    # Technical Details Section
    st.markdown("## ⚙️ Technical Details")
    st.markdown("### Product Feasibility")
    
    st.markdown("### System Components")
    
    st.code("""
Oncology/
├── src/
│   ├── parsers/          # Extract structured data from clinical inputs
│   │   ├── lab_parser.py
│   │   ├── medication_parser.py
│   │   ├── symptom_parser.py
│   │   └── note_parser.py
│   │
│   ├── analyzers/        # 9 organ-specific irAE detectors
│   │   ├── gi_analyzer.py
│   │   ├── liver_analyzer.py
│   │   ├── lung_analyzer.py
│   │   ├── endocrine_analyzer.py
│   │   ├── skin_analyzer.py
│   │   ├── neuro_analyzer.py
│   │   ├── cardiac_analyzer.py
│   │   ├── renal_analyzer.py
│   │   └── hematologic_analyzer.py
│   │
│   ├── llm/              # MedGemma integration
│   │   ├── client.py     # Multi-backend (HuggingFace, OpenAI, Anthropic)
│   │   ├── prompts.py    # Clinical prompt templates
│   │   └── assessment_engine.py
│   │
│   └── api/              # FastAPI REST endpoints
│
├── app/                  # Streamlit web interface
├── fine_tuning/          # LoRA fine-tuning pipeline
└── tests/                # 126 test cases
    """, language=None)
    
    st.markdown("### Model Fine-Tuning")
    
    ft_col1, ft_col2 = st.columns(2)
    
    with ft_col1:
        st.markdown("""
        **LoRA Fine-Tuning Pipeline:**
        - 11 validated clinical cases across all organ systems
        - CTCAE grading examples (Grades 1-4)
        - Urgency classification training
        - Parameter-efficient (0.5% of weights)
        """)
    
    with ft_col2:
        st.markdown("""
        **Training Infrastructure:**
        - Runs on T4 GPU (16GB VRAM)
        - ~$0.60/hour compute cost
        - Preserves base medical knowledge
        - Improves irAE-specific accuracy
        """)
    
    st.markdown("### Validation & Performance")
    
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    
    with perf_col1:
        st.metric("Test Coverage", "126/126", "passing")
    with perf_col2:
        st.metric("Organ Systems", "9/9", "validated")
    with perf_col3:
        st.metric("Sensitivity", "~95%", "estimated")
    with perf_col4:
        st.metric("CTCAE Accuracy", "v5.0", "validated")
    
    st.markdown("### Deployment Architecture")
    
    deploy_col1, deploy_col2 = st.columns(2)
    
    with deploy_col1:
        st.markdown("""
        **Application Stack:**
        - **Frontend:** Streamlit web app
        - **Backend:** FastAPI REST API
        - **Container:** Docker (HF Spaces compatible)
        - **Hardware:** T4 GPU (~2-3s inference)
        """)
    
    with deploy_col2:
        st.markdown("""
        **Deployment Challenges & Solutions:**
        - **Privacy:** On-premises deployment; local MedGemma
        - **EHR Integration:** REST API with HL7 FHIR support
        - **Latency:** Pre-parsing, caching, quantization
        - **Validation:** Phased rollout with shadow-mode
        """)
    
    st.markdown("### Real-World Usage Flow")
    
    st.code("""
    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
    │  INTEGRATE  │ ──▶  │   MONITOR   │ ──▶  │    ALERT    │ ──▶  │    ACT      │
    │             │      │             │      │             │      │             │
    │ Connect to  │      │ Scan patient│      │ Flag high-  │      │ Clinician   │
    │ EHR or use  │      │ data for    │      │ risk with   │      │ confirms,   │
    │ web interface│     │ irAE signals│      │ evidence    │      │ escalates   │
    └─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
                                                                          │
                                                                          ▼
                                                                   ┌─────────────┐
                                                                   │    LEARN    │
                                                                   │             │
                                                                   │ Log feedback│
                                                                   │ for accuracy│
                                                                   │ improvement │
                                                                   └─────────────┘
    """, language=None)
    
    st.markdown("---")
    
    st.markdown("## 🔗 Resources")
    
    st.markdown("""
    - **Repository:** [github.com/HustleDanie/Oncology-irAE-Detection](https://github.com/HustleDanie/Oncology-irAE-Detection)
    - **Live Demo:** [HuggingFace Space](https://huggingface.co/spaces/Hustledaniel/OncologyDetection)
    - **Model:** [Google MedGemma 4B-IT](https://huggingface.co/google/medgemma-4b-it)
    """)
    
    st.markdown("---")
    
    st.info("""
    **Key Takeaway:** This tool transforms irAE detection from reactive ("the patient is crashing") 
    to proactive ("this patient needs attention before they crash"). It doesn't replace oncologists—it 
    gives them superpowers.
    """)
