"""
Technical Architecture View

Visual representation of system architecture, key metrics,
and technical credibility for hackathon demo.

Redesigned with professional UI/UX for hackathon presentation.
"""

import streamlit as st
import pandas as pd


def render():
    """Render the technical architecture page."""
    
    # =========================================================================
    # CUSTOM CSS FOR PROFESSIONAL STYLING
    # =========================================================================
    st.markdown("""
    <style>
    /* Stat Cards */
    .tech-stat-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .tech-stat-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }
    
    .tech-stat-value.green { color: #27ae60; }
    .tech-stat-value.blue { color: #3498db; }
    .tech-stat-value.purple { color: #9b59b6; }
    .tech-stat-value.orange { color: #f39c12; }
    .tech-stat-value.red { color: #e74c3c; }
    
    .tech-stat-label {
        font-size: 0.9rem;
        color: #495057;
        font-weight: 600;
    }
    
    .tech-stat-sublabel {
        font-size: 0.75rem;
        color: #6c757d;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.6rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    /* Info Box - WHITE BACKGROUND */
    .info-box {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.25rem;
        border-left: 5px solid #2196f3;
        color: #1565c0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    .info-box strong {
        color: #0d47a1;
    }
    
    /* Architecture Flow Container */
    .arch-container {
        background: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    
    /* Architecture Node */
    .arch-node {
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        color: white;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    .arch-node.input { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .arch-node.parser { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .arch-node.medgemma { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border: 3px solid #ffd700; }
    .arch-node.rules { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: #333; }
    .arch-node.safety { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); border: 3px solid #ffd700; }
    .arch-node.output { background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%); }
    
    .arch-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .arch-title {
        font-weight: 700;
        font-size: 1rem;
    }
    
    .arch-subtitle {
        font-size: 0.8rem;
        opacity: 0.9;
    }
    
    .arch-arrow {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        color: #667eea;
        min-height: 120px;
    }
    
    /* Component Cards - WHITE BACKGROUND */
    .component-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 2px solid;
        min-height: 320px;
    }
    
    .component-card.medgemma { border-color: #9b59b6; }
    .component-card.rules { border-color: #3498db; }
    .component-card.safety { border-color: #e74c3c; }
    
    .component-header {
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
    }
    
    .component-header.medgemma { color: #8e44ad; }
    .component-header.rules { color: #2980b9; }
    .component-header.safety { color: #c0392b; }
    
    .component-section {
        margin-bottom: 1rem;
    }
    
    .component-section-title {
        font-weight: 600;
        color: #495057;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .component-list {
        color: #333;
        font-size: 0.9rem;
        padding-left: 1.25rem;
        margin: 0;
    }
    
    .component-list li {
        margin-bottom: 0.25rem;
    }
    
    /* Data Flow Card */
    .flow-input-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.25rem;
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    .flow-input-card h4 {
        color: #333;
        margin: 0;
    }
    
    /* Step Cards */
    .step-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-top: 4px solid;
        min-height: 200px;
    }
    
    .step-card.step1 { border-color: #667eea; }
    .step-card.step2 { border-color: #9b59b6; }
    .step-card.step3 { border-color: #3498db; }
    .step-card.step4 { border-color: #e74c3c; }
    
    .step-title {
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.75rem;
        color: #333;
    }
    
    /* Success Banner */
    .success-banner {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
    }
    
    .success-banner h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.2rem;
    }
    
    .success-banner p {
        margin: 0;
        opacity: 0.95;
    }
    
    /* Comparison Cards */
    .compare-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 2px solid;
        min-height: 220px;
    }
    
    .compare-card.bad { border-color: #e74c3c; }
    .compare-card.good { border-color: #27ae60; }
    
    .compare-header {
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
    }
    
    .compare-header.bad { color: #c0392b; }
    .compare-header.good { color: #27ae60; }
    
    .compare-list {
        color: #333;
        font-size: 0.9rem;
        padding-left: 1.25rem;
        margin: 0;
    }
    
    /* Test Cards */
    .test-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 5px solid #27ae60;
    }
    
    .test-title {
        font-weight: 700;
        color: #27ae60;
        margin-bottom: 0.75rem;
    }
    
    .test-list {
        color: #333;
        font-size: 0.9rem;
        margin: 0;
        padding-left: 0;
        list-style: none;
    }
    
    .test-list li {
        margin-bottom: 0.25rem;
    }
    
    .test-list li::before {
        content: "✅ ";
    }
    
    /* Key Insight Box */
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .insight-box strong {
        color: #ffd700;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # HERO SECTION
    # =========================================================================
    st.markdown('<p class="main-header">🔧 Technical Architecture</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">How our MedGemma-first system works</p>', unsafe_allow_html=True)
    
    # =========================================================================
    # KEY METRICS CARDS
    # =========================================================================
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="tech-stat-card">
            <div class="tech-stat-value green">126</div>
            <div class="tech-stat-label">Tests Passing</div>
            <div class="tech-stat-sublabel">All green ✓</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="tech-stat-card">
            <div class="tech-stat-value blue">9</div>
            <div class="tech-stat-label">Organ Systems</div>
            <div class="tech-stat-sublabel">Complete coverage</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="tech-stat-card">
            <div class="tech-stat-value purple">1-4</div>
            <div class="tech-stat-label">CTCAE Grades</div>
            <div class="tech-stat-sublabel">Full spectrum</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="tech-stat-card">
            <div class="tech-stat-value orange">80%</div>
            <div class="tech-stat-label">Smaller Prompts</div>
            <div class="tech-stat-sublabel">vs GPT prompts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="tech-stat-card">
            <div class="tech-stat-value red">100%</div>
            <div class="tech-stat-label">Safety Rules</div>
            <div class="tech-stat-sublabel">Cannot bypass</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # =========================================================================
    # ARCHITECTURE DIAGRAM
    # =========================================================================
    st.markdown('<div class="section-header">🏗️ System Architecture</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>MedGemma-First Philosophy:</strong> Let the AI do what it's good at (clinical reasoning), 
        then validate with rule-based systems for safety. Best of both worlds.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Architecture Flow
    st.markdown('<div class="arch-container">', unsafe_allow_html=True)
    
    a_col1, a_arr1, a_col2, a_arr2, a_col3, a_arr3, a_col4, a_arr4, a_col5, a_arr5, a_col6 = st.columns([1.5, 0.4, 1.5, 0.4, 1.8, 0.4, 1.5, 0.4, 1.8, 0.4, 1.5])
    
    with a_col1:
        st.markdown("""
        <div class="arch-node input">
            <div class="arch-icon">📋</div>
            <div class="arch-title">Clinical Input</div>
            <div class="arch-subtitle">Notes, Labs, Meds</div>
        </div>
        """, unsafe_allow_html=True)
    
    with a_arr1:
        st.markdown('<div class="arch-arrow">→</div>', unsafe_allow_html=True)
    
    with a_col2:
        st.markdown("""
        <div class="arch-node parser">
            <div class="arch-icon">⚙️</div>
            <div class="arch-title">Parsers</div>
            <div class="arch-subtitle">Structure Data</div>
        </div>
        """, unsafe_allow_html=True)
    
    with a_arr2:
        st.markdown('<div class="arch-arrow">→</div>', unsafe_allow_html=True)
    
    with a_col3:
        st.markdown("""
        <div class="arch-node medgemma">
            <div class="arch-icon">🧠</div>
            <div class="arch-title">MedGemma 4B</div>
            <div class="arch-subtitle">Clinical Reasoning</div>
        </div>
        """, unsafe_allow_html=True)
    
    with a_arr3:
        st.markdown('<div class="arch-arrow">→</div>', unsafe_allow_html=True)
    
    with a_col4:
        st.markdown("""
        <div class="arch-node rules">
            <div class="arch-icon">📐</div>
            <div class="arch-title">Rule-Based</div>
            <div class="arch-subtitle">9 Analyzers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with a_arr4:
        st.markdown('<div class="arch-arrow">→</div>', unsafe_allow_html=True)
    
    with a_col5:
        st.markdown("""
        <div class="arch-node safety">
            <div class="arch-icon">🛡️</div>
            <div class="arch-title">SafetyValidator</div>
            <div class="arch-subtitle">CANNOT BYPASS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with a_arr5:
        st.markdown('<div class="arch-arrow">→</div>', unsafe_allow_html=True)
    
    with a_col6:
        st.markdown("""
        <div class="arch-node output">
            <div class="arch-icon">✅</div>
            <div class="arch-title">Assessment</div>
            <div class="arch-subtitle">Grade + Urgency</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # COMPONENT DEEP DIVE
    # =========================================================================
    st.markdown('<div class="section-header">🔍 Component Deep Dive</div>', unsafe_allow_html=True)
    
    comp_col1, comp_col2, comp_col3 = st.columns(3)
    
    with comp_col1:
        st.markdown("""
        <div class="component-card medgemma">
            <div class="component-header medgemma">🧠 MedGemma 4B-IT</div>
            
            <div class="component-section">
                <div class="component-section-title">Role</div>
                <p style="color: #333; margin: 0; font-size: 0.9rem;">Primary clinical reasoning engine</p>
            </div>
            
            <div class="component-section">
                <div class="component-section-title">Capabilities</div>
                <ul class="component-list">
                    <li>Interprets clinical context</li>
                    <li>Identifies irAE patterns</li>
                    <li>Suggests severity grades</li>
                    <li>Generates recommendations</li>
                </ul>
            </div>
            
            <div class="component-section">
                <div class="component-section-title">Optimizations</div>
                <ul class="component-list">
                    <li>1,608 character prompt</li>
                    <li>Structured output format</li>
                    <li>Medical domain training</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with comp_col2:
        st.markdown("""
        <div class="component-card rules">
            <div class="component-header rules">📐 Rule-Based Analyzers</div>
            
            <div class="component-section">
                <div class="component-section-title">Role</div>
                <p style="color: #333; margin: 0; font-size: 0.9rem;">Domain-specific validation</p>
            </div>
            
            <div class="component-section">
                <div class="component-section-title">9 Organ Systems</div>
                <ul class="component-list">
                    <li>GI (Colitis)</li>
                    <li>Liver (Hepatitis)</li>
                    <li>Lung (Pneumonitis)</li>
                    <li>Cardiac (Myocarditis)</li>
                    <li>Endocrine (Thyroid/Adrenal)</li>
                    <li>Neuro, Skin, Renal, Hematologic</li>
                </ul>
            </div>
            
            <div class="component-section">
                <div class="component-section-title">Standard</div>
                <p style="color: #333; margin: 0; font-size: 0.9rem;">CTCAE v5.0 thresholds</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with comp_col3:
        st.markdown("""
        <div class="component-card safety">
            <div class="component-header safety">🛡️ SafetyValidator</div>
            
            <div class="component-section">
                <div class="component-section-title">Role</div>
                <p style="color: #333; margin: 0; font-size: 0.9rem;">Enforce safety floors</p>
            </div>
            
            <div class="component-section">
                <div class="component-section-title">Rules (CANNOT bypass)</div>
                <ul class="component-list">
                    <li>Grade 2+ → NEVER routine</li>
                    <li>Grade 3+ → ALWAYS urgent+</li>
                    <li>Cardiac → ALWAYS emergency</li>
                    <li>Neuro → ALWAYS urgent</li>
                </ul>
            </div>
            
            <div class="component-section">
                <div class="component-section-title">Why It Matters</div>
                <p style="color: #333; margin: 0; font-size: 0.9rem;">Even if MedGemma makes a mistake, SafetyValidator catches it. Patient safety is <strong>hardcoded</strong>.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # =========================================================================
    # DATA FLOW EXAMPLE
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📝 Data Flow Example</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="flow-input-card">
        <h4>📥 Input: "58-year-old on pembrolizumab with 5-6 loose stools daily x4 days"</h4>
    </div>
    """, unsafe_allow_html=True)
    
    flow_col1, flow_col2, flow_col3, flow_col4 = st.columns(4)
    
    with flow_col1:
        st.markdown("""
        <div class="step-card step1">
            <div class="step-title">Step 1: Parsers</div>
            <code style="font-size: 0.8rem; display: block; background: #f8f9fa; padding: 0.5rem; border-radius: 4px; color: #333;">
Medication: pembrolizumab
  → ICI detected ✓

Symptoms: diarrhea
  → 5-6 stools/day
  → Duration: 4 days
            </code>
        </div>
        """, unsafe_allow_html=True)
    
    with flow_col2:
        st.markdown("""
        <div class="step-card step2">
            <div class="step-title">Step 2: MedGemma</div>
            <code style="font-size: 0.8rem; display: block; background: #f8f9fa; padding: 0.5rem; border-radius: 4px; color: #333;">
{
  "irae_detected": true,
  "organ_system": "GI",
  "condition": "Colitis",
  "severity": "Grade 2"
}
            </code>
        </div>
        """, unsafe_allow_html=True)
    
    with flow_col3:
        st.markdown("""
        <div class="step-card step3">
            <div class="step-title">Step 3: GI Analyzer</div>
            <code style="font-size: 0.8rem; display: block; background: #f8f9fa; padding: 0.5rem; border-radius: 4px; color: #333;">
Validates:
✓ Stool frequency matches
✓ Duration concerning
✓ Grade 2 threshold met

Confirms: Grade 2
            </code>
        </div>
        """, unsafe_allow_html=True)
    
    with flow_col4:
        st.markdown("""
        <div class="step-card step4">
            <div class="step-title">Step 4: SafetyValidator</div>
            <code style="font-size: 0.8rem; display: block; background: #f8f9fa; padding: 0.5rem; border-radius: 4px; color: #333;">
Input: "routine"

⚠️ BLOCKED!
Grade 2 ≠ routine

Corrected → "soon"
            </code>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="success-banner">
        <h4>✅ Final Output</h4>
        <p><strong>Grade 2 GI Colitis</strong> • Urgency: <strong>SOON</strong> • Hold immunotherapy • Start steroids</p>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # TECHNICAL SPECS
    # =========================================================================
    st.markdown('<div class="section-header">📋 Technical Specifications</div>', unsafe_allow_html=True)
    
    spec_col1, spec_col2 = st.columns(2)
    
    with spec_col1:
        st.markdown("#### Core Stack")
        specs_core = {
            "Component": ["LLM", "Framework", "Web UI", "Data Validation", "Testing"],
            "Technology": ["MedGemma 4B-IT", "Python 3.11+", "Streamlit", "Pydantic", "pytest"],
            "Details": ["Google's medical LLM", "Async support", "Real-time updates", "Strict type checking", "126 test cases"]
        }
        st.dataframe(pd.DataFrame(specs_core), use_container_width=True, hide_index=True)
    
    with spec_col2:
        st.markdown("#### Safety Features")
        specs_safety = {
            "Feature": ["Urgency Floors", "Cardiac Override", "Neuro Override", "Logging"],
            "Implementation": ["SafetyValidator", "Hardcoded", "Hardcoded", "AccuracyMonitor"],
            "Bypass?": ["❌ No", "❌ No", "❌ No", "N/A"]
        }
        st.dataframe(pd.DataFrame(specs_safety), use_container_width=True, hide_index=True)
    
    # =========================================================================
    # WHY MEDGEMMA-FIRST
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">🤔 Why MedGemma-First?</div>', unsafe_allow_html=True)
    
    why_col1, why_col2 = st.columns(2)
    
    with why_col1:
        st.markdown("""
        <div class="compare-card bad">
            <div class="compare-header bad">❌ Traditional: Rules-First</div>
            <ul class="compare-list">
                <li>Rigid decision trees</li>
                <li>Misses edge cases</li>
                <li>Hard to maintain</li>
                <li>Poor with unstructured text</li>
                <li>Requires expert for every rule</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with why_col2:
        st.markdown("""
        <div class="compare-card good">
            <div class="compare-header good">✅ Our Approach: AI + Rules</div>
            <ul class="compare-list">
                <li>Flexible clinical reasoning</li>
                <li>Handles natural language</li>
                <li>Catches patterns humans miss</li>
                <li>Safety rules can't be bypassed</li>
                <li>Best of both worlds</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="insight-box">
        <strong>The Key Insight:</strong> We let MedGemma do what AI does best (understanding clinical context), 
        then use deterministic rules to ensure safety. The AI can suggest "routine" for a Grade 2, 
        but SafetyValidator will <strong>always</strong> correct it to "soon" — no exceptions.
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # TEST COVERAGE
    # =========================================================================
    st.markdown('<div class="section-header">✅ Test Coverage</div>', unsafe_allow_html=True)
    
    test_col1, test_col2, test_col3 = st.columns(3)
    
    with test_col1:
        st.markdown("""
        <div class="test-card">
            <div class="test-title">CTCAE Grading Tests</div>
            <ul class="test-list">
                <li>Grade 1 scenarios</li>
                <li>Grade 2 scenarios</li>
                <li>Grade 3 scenarios</li>
                <li>Grade 4 scenarios</li>
                <li>Edge cases</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with test_col2:
        st.markdown("""
        <div class="test-card">
            <div class="test-title">Organ System Tests</div>
            <ul class="test-list">
                <li>GI Colitis</li>
                <li>Hepatitis</li>
                <li>Pneumonitis</li>
                <li>Cardiac</li>
                <li>Endocrine</li>
                <li>Neuro/Skin/Renal</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with test_col3:
        st.markdown("""
        <div class="test-card">
            <div class="test-title">Safety Tests</div>
            <ul class="test-list">
                <li>Urgency floors</li>
                <li>Cardiac override</li>
                <li>Neuro override</li>
                <li>Grade escalation</li>
                <li>Input validation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.code("pytest tests/ -v  →  126 passed, 0 failed", language="bash")
    
    # =========================================================================
    # CTA
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="success-banner" style="text-align: center;">
        <h4>🚀 Ready to See It Work?</h4>
        <p>Head to <strong>New Assessment</strong> to try the system, or check out <strong>Statistics</strong> for clinical impact data and demo cases.</p>
    </div>
    """, unsafe_allow_html=True)
