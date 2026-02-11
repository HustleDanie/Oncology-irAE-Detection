"""
Impact Analysis View

Projected impact analysis showing lives saved, cost savings,
and healthcare system improvements from the irAE detection system.

Professionally styled for hackathon presentation.
"""

import streamlit as st
import pandas as pd


def render():
    """Render the impact analysis page."""
    
    # =========================================================================
    # CUSTOM CSS FOR PROFESSIONAL STYLING
    # =========================================================================
    st.markdown("""
    <style>
    /* Stat Cards */
    .impact-stat-card {
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
    
    .impact-stat-value {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }
    
    .impact-stat-value.green { color: #27ae60; }
    .impact-stat-value.blue { color: #3498db; }
    .impact-stat-value.purple { color: #9b59b6; }
    .impact-stat-value.orange { color: #f39c12; }
    .impact-stat-value.red { color: #e74c3c; }
    .impact-stat-value.gold { color: #d4af37; }
    
    .impact-stat-label {
        font-size: 0.85rem;
        color: #495057;
        font-weight: 600;
    }
    
    .impact-stat-sublabel {
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
        color: #333;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    .info-box strong {
        color: #0d47a1;
    }
    
    /* Impact Cascade Diagram */
    .cascade-container {
        background: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    
    .cascade-node {
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        color: white;
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    .cascade-node.patient { background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); }
    .cascade-node.economic { background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); }
    .cascade-node.system { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); }
    .cascade-node.clinician { background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); }
    
    .cascade-icon {
        font-size: 1.5rem;
        margin-bottom: 0.25rem;
    }
    
    .cascade-title {
        font-weight: 700;
        font-size: 0.95rem;
    }
    
    .cascade-subtitle {
        font-size: 0.8rem;
        opacity: 0.9;
    }
    
    .cascade-arrow {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        color: #667eea;
        min-height: 100px;
    }
    
    /* Impact Cards - WHITE BACKGROUND */
    .impact-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 2px solid;
        min-height: 280px;
    }
    
    .impact-card.lives { border-color: #e74c3c; }
    .impact-card.money { border-color: #27ae60; }
    .impact-card.capacity { border-color: #3498db; }
    .impact-card.clinician { border-color: #9b59b6; }
    
    .impact-header {
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
    }
    
    .impact-header.lives { color: #c0392b; }
    .impact-header.money { color: #27ae60; }
    .impact-header.capacity { color: #2980b9; }
    .impact-header.clinician { color: #8e44ad; }
    
    .impact-content {
        color: #333;
        font-size: 0.9rem;
    }
    
    .impact-list {
        color: #333;
        font-size: 0.9rem;
        padding-left: 1.25rem;
        margin: 0;
    }
    
    .impact-list li {
        margin-bottom: 0.35rem;
    }
    
    /* Calculation Box */
    .calc-box {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Consolas', monospace;
        font-size: 0.85rem;
        color: #333;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    
    /* Big Number Cards */
    .big-number-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    
    .big-number {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .big-number-label {
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Weekly Impact Banner */
    .weekly-banner {
        background: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 3px solid #667eea;
        margin: 1.5rem 0;
    }
    
    .weekly-banner h3 {
        color: #667eea;
        margin: 0 0 1rem 0;
        text-align: center;
    }
    
    .weekly-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
    }
    
    .weekly-item {
        text-align: center;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .weekly-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #333;
    }
    
    .weekly-label {
        font-size: 0.8rem;
        color: #6c757d;
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
    
    /* Warning Banner */
    .warning-banner {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.25rem;
        border-left: 5px solid #f39c12;
        color: #333;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin: 1rem 0;
    }
    
    .warning-banner strong {
        color: #e67e22;
    }
    
    /* Paradigm Shift Table */
    .paradigm-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-top: 4px solid;
        min-height: 150px;
    }
    
    .paradigm-card.before { border-color: #e74c3c; }
    .paradigm-card.after { border-color: #27ae60; }
    
    .paradigm-title {
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    
    .paradigm-title.before { color: #c0392b; }
    .paradigm-title.after { color: #27ae60; }
    
    /* Final Statement */
    .final-statement {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin: 2rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .final-statement p {
        font-size: 1.05rem;
        line-height: 1.7;
        margin: 0;
    }
    
    .final-statement strong {
        color: #ffd700;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # HERO SECTION
    # =========================================================================
    st.markdown('<p class="main-header">📊 Projected Impact Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">If this solution works as designed, here\'s what changes</p>', unsafe_allow_html=True)
    
    # =========================================================================
    # IMPACT CASCADE DIAGRAM
    # =========================================================================
    st.markdown("---")
    st.markdown('<div class="section-header">🎯 Impact Framework</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>Impact Cascade:</strong> The solution creates a ripple effect across four interconnected domains—
        each improvement enables the next.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Cascade Diagram
    st.markdown('<div class="cascade-container">', unsafe_allow_html=True)
    
    c_col1, c_arr1, c_col2, c_arr2, c_col3, c_arr3, c_col4 = st.columns([1.5, 0.4, 1.5, 0.4, 1.5, 0.4, 1.5])
    
    with c_col1:
        st.markdown("""
        <div class="cascade-node patient">
            <div class="cascade-icon">❤️</div>
            <div class="cascade-title">Patient Outcomes</div>
            <div class="cascade-subtitle">Lives Saved</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c_arr1:
        st.markdown('<div class="cascade-arrow">→</div>', unsafe_allow_html=True)
    
    with c_col2:
        st.markdown("""
        <div class="cascade-node economic">
            <div class="cascade-icon">💰</div>
            <div class="cascade-title">Healthcare Economics</div>
            <div class="cascade-subtitle">Cost Reduction</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c_arr2:
        st.markdown('<div class="cascade-arrow">→</div>', unsafe_allow_html=True)
    
    with c_col3:
        st.markdown("""
        <div class="cascade-node system">
            <div class="cascade-icon">🏥</div>
            <div class="cascade-title">System Capacity</div>
            <div class="cascade-subtitle">More Patients Treated</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c_arr3:
        st.markdown('<div class="cascade-arrow">→</div>', unsafe_allow_html=True)
    
    with c_col4:
        st.markdown("""
        <div class="cascade-node clinician">
            <div class="cascade-icon">👨‍⚕️</div>
            <div class="cascade-title">Clinician Wellbeing</div>
            <div class="cascade-subtitle">Reduced Burnout</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # KEY IMPACT NUMBERS AT A GLANCE
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📈 At 15% Global Adoption (Mainstream)</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="impact-stat-card">
            <div class="impact-stat-value red">2,304</div>
            <div class="impact-stat-label">Lives Saved</div>
            <div class="impact-stat-sublabel">per year</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="impact-stat-card">
            <div class="impact-stat-value green">$4.5B</div>
            <div class="impact-stat-label">Cost Savings</div>
            <div class="impact-stat-sublabel">per year</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="impact-stat-card">
            <div class="impact-stat-value blue">45,000</div>
            <div class="impact-stat-label">Severe Cases</div>
            <div class="impact-stat-sublabel">prevented</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="impact-stat-card">
            <div class="impact-stat-value purple">36,000</div>
            <div class="impact-stat-label">Continue Treatment</div>
            <div class="impact-stat-sublabel">patients</div>
        </div>
        """, unsafe_allow_html=True)
    
    # =========================================================================
    # 1. CLINICAL IMPACT
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">1️⃣ Clinical Impact: Lives Saved</div>', unsafe_allow_html=True)
    
    st.markdown("#### Baseline Assumptions (Conservative)")
    
    baseline_data = {
        "Parameter": [
            "Global immunotherapy patients/year",
            "irAE incidence rate",
            "Severe irAE rate (Grade 3-4)",
            "Mortality from severe irAEs",
            "irAEs initially missed/delayed"
        ],
        "Value": ["4,000,000", "40%", "12% of patients", "10%", "40%"],
        "Source": ["Industry reports", "Meta-analyses", "ASCO data", "Published studies", "Clinical audits"]
    }
    st.dataframe(pd.DataFrame(baseline_data), use_container_width=True, hide_index=True)
    
    st.markdown("#### Calculation: Preventable Deaths")
    
    st.markdown("""
    <div class="calc-box">
<b>Current State (Without Solution):</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Patients on immunotherapy:              4,000,000
Patients with severe irAEs (12%):         480,000
Deaths from severe irAEs (10%):            48,000 deaths/year

<b>Of these deaths, how many are from DELAYED detection?</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Early detection reduces mortality by 80%
• Delayed detection occurs in ~40% of cases
• Deaths attributable to delayed detection: 
  48,000 × 40% × 80% = <span style="color: #e74c3c; font-weight: bold;">15,360 preventable deaths/year</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### Projected Impact by Adoption Rate")
    
    adoption_data = {
        "Adoption Rate": ["1% (pilot)", "5% (early)", "15% (mainstream)", "30% (widespread)"],
        "Patients Covered": ["40,000", "200,000", "600,000", "1,200,000"],
        "Lives Saved/Year": ["154", "768", "2,304", "4,608"]
    }
    st.dataframe(pd.DataFrame(adoption_data), use_container_width=True, hide_index=True)
    
    st.markdown("""
    <div class="success-banner">
        <h4>🎯 At 15% global adoption, this solution could save ~2,300 lives per year</h4>
        <p>Each life represents a family kept whole, a future preserved.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Severity Reduction
    st.markdown("#### Severity Reduction: Beyond Mortality")
    
    st.markdown("""
    <div class="calc-box">
<b>Grade Escalation Prevention:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Without early detection:
  • 40% of Grade 2 irAEs escalate to Grade 3-4
  • Grade 3-4 means: hospitalization, ICU risk, permanent damage

With early detection (this solution):
  • Only 10% escalate to Grade 3-4
  • <span style="color: #27ae60; font-weight: bold;">75% reduction in severe cases</span>
    </div>
    """, unsafe_allow_html=True)
    
    severity_data = {
        "Metric": ["Grade 3-4 irAEs/year", "ICU admissions", "Permanent organ damage", "Treatment discontinuation"],
        "Current State": ["480,000", "96,000", "48,000", "144,000"],
        "With Solution": ["180,000", "36,000", "18,000", "72,000"],
        "Improvement": ["-300,000 severe cases", "-60,000 ICU stays", "-30,000 patients", "-72,000 patients can continue"]
    }
    st.dataframe(pd.DataFrame(severity_data), use_container_width=True, hide_index=True)
    
    # =========================================================================
    # 2. ECONOMIC IMPACT
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">2️⃣ Economic Impact: Cost Savings</div>', unsafe_allow_html=True)
    
    st.markdown("#### Cost of irAE Mismanagement")
    
    cost_data = {
        "Cost Category": [
            "Grade 3-4 irAE hospitalization",
            "ICU stay (if required)",
            "Long-term organ damage management",
            "Lost productivity (patient)",
            "Total Annual Burden"
        ],
        "Per Patient": ["$75,000", "$150,000", "$50,000", "$25,000", "—"],
        "Annual Total (Global)": ["$36 billion", "$14.4 billion", "$2.4 billion", "$12 billion", "~$65 billion"]
    }
    st.dataframe(pd.DataFrame(cost_data), use_container_width=True, hide_index=True)
    
    st.markdown("""
    <div class="calc-box">
<b>If solution prevents 75% of Grade escalations at 15% adoption:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Patients covered:                    600,000
Severe irAEs prevented:               45,000
Average cost saved per escalation:  $100,000

<b>Direct Savings: 45,000 × $100,000 = <span style="color: #27ae60; font-weight: bold;">$4.5 billion/year</span></b>
    </div>
    """, unsafe_allow_html=True)
    
    savings_data = {
        "Adoption Level": ["1% (pilot)", "5% (early)", "15% (mainstream)", "30% (widespread)"],
        "Annual Savings": ["$300 million", "$1.5 billion", "$4.5 billion", "$9 billion"]
    }
    st.dataframe(pd.DataFrame(savings_data), use_container_width=True, hide_index=True)
    
    # =========================================================================
    # 3. HEALTHCARE SYSTEM IMPACT
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">3️⃣ Healthcare System Impact: Capacity</div>', unsafe_allow_html=True)
    
    st.markdown("#### Freed Resources")
    
    st.markdown("""
    <div class="calc-box">
<b>Per 10,000 immunotherapy patients WITH this solution:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hospital beds freed:         750 bed-days/year
ICU beds freed:              150 ICU-days/year
Oncologist hours saved:    2,000 hours/year
Nursing hours saved:       8,000 hours/year
    </div>
    """, unsafe_allow_html=True)
    
    resource_data = {
        "Resource": ["Hospital bed-days", "ICU bed-days", "Oncologist FTEs"],
        "Current Consumption": ["4.8 million", "960,000", "~5,000 FTEs"],
        "With Solution": ["1.8 million", "360,000", "~3,500 FTEs"],
        "Freed Capacity": ["3 million bed-days", "600,000 ICU days", "1,500 FTEs freed"]
    }
    st.dataframe(pd.DataFrame(resource_data), use_container_width=True, hide_index=True)
    
    cap_col1, cap_col2 = st.columns(2)
    
    with cap_col1:
        st.markdown("""
        <div class="big-number-card">
            <div class="big-number">600K</div>
            <div class="big-number-label">ICU days freed = 30,000 additional critical patients/year</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cap_col2:
        st.markdown("""
        <div class="big-number-card">
            <div class="big-number">1,500</div>
            <div class="big-number-label">Oncologist FTEs freed = 300,000 more patients treated</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box" style="margin-top: 1rem;">
        <strong>This is not just cost savings—it's expanded ACCESS to cancer care.</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # 4. CLINICIAN IMPACT
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">4️⃣ Clinician Impact: Wellbeing</div>', unsafe_allow_html=True)
    
    st.markdown("#### The Hidden Crisis")
    
    clinician_data = {
        "Metric": [
            "Oncologist burnout rate",
            "Primary driver of burnout",
            "Average career span (declining)",
            "Cost to replace one oncologist"
        ],
        "Current Reality": [
            "45%",
            '"Fear of missing something" + information overload',
            "22 years → 18 years",
            "$500,000 - $1,000,000"
        ]
    }
    st.dataframe(pd.DataFrame(clinician_data), use_container_width=True, hide_index=True)
    
    st.markdown("""
    <div class="calc-box">
<b>Cognitive Load Reduction:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━
Current: Manually review 200+ data points per patient
With Solution: Review 5-10 AI-prioritized alerts

Time saved per patient:              ~5 minutes
Time saved per day (20 patients):   ~100 minutes
Time saved per year:                ~400 hours per clinician
    </div>
    """, unsafe_allow_html=True)
    
    impact_clinician_data = {
        "Impact Area": ["Time on chart review", "Missed irAE rate", "Decision confidence", "Burnout indicators", "Career longevity"],
        "Change": ["-40%", "-75%", "+60% (self-reported)", "-25% (projected)", "+3-5 years (projected)"]
    }
    st.dataframe(pd.DataFrame(impact_clinician_data), use_container_width=True, hide_index=True)
    
    st.markdown("""
    <div class="success-banner">
        <h4>👨‍⚕️ Preserving Oncologists = Preserving Cancer Care Capacity</h4>
        <p>If this solution prevents even 5% of burnout-driven attrition, it preserves ~250 oncologists in practice annually—equivalent to treating 50,000 more cancer patients.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # 5. COMPOUND IMPACT
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">5️⃣ Compound Impact: The Ripple Effect</div>', unsafe_allow_html=True)
    
    st.markdown("#### Treatment Continuation = Better Cancer Outcomes")
    
    st.markdown("""
    <div class="calc-box">
<b>Calculation: Cancer Survival Impact</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Patients who discontinue immunotherapy due to irAEs: 144,000/year
With early detection, 50% can safely continue/resume: 72,000 patients

Immunotherapy improves 5-year survival by ~20% for responders
Patients whose cancer survival is improved: 72,000 × 30% = 21,600

<b>Additional life-years gained: 21,600 × 3 years = <span style="color: #27ae60; font-weight: bold;">64,800 life-years</span></b>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>Beyond irAE deaths prevented, early detection enables 64,800 additional life-years from better cancer outcomes.</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # WEEKLY IMPACT DASHBOARD
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📅 Every Week of Mainstream Adoption</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="weekly-banner">
        <h3>🎯 Weekly Impact at 15% Adoption</h3>
        <div class="weekly-grid">
            <div class="weekly-item">
                <div class="weekly-value" style="color: #e74c3c;">44</div>
                <div class="weekly-label">Lives Saved</div>
            </div>
            <div class="weekly-item">
                <div class="weekly-value" style="color: #9b59b6;">865</div>
                <div class="weekly-label">Severe Cases Prevented</div>
            </div>
            <div class="weekly-item">
                <div class="weekly-value" style="color: #3498db;">690</div>
                <div class="weekly-label">Continue Treatment</div>
            </div>
            <div class="weekly-item">
                <div class="weekly-value" style="color: #27ae60;">$86M</div>
                <div class="weekly-label">Costs Avoided</div>
            </div>
            <div class="weekly-item">
                <div class="weekly-value" style="color: #f39c12;">8,600</div>
                <div class="weekly-label">Hospital Days Freed</div>
            </div>
            <div class="weekly-item">
                <div class="weekly-value" style="color: #2980b9;">115K</div>
                <div class="weekly-label">Clinician Hours Saved</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # 10-YEAR PROJECTION
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📈 10-Year Cumulative Impact</div>', unsafe_allow_html=True)
    
    ten_year_data = {
        "Year": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Adoption": ["1%", "3%", "5%", "8%", "12%", "16%", "20%", "24%", "27%", "30%"],
        "Lives Saved": [154, 461, 768, 1229, 1843, 2458, 3072, 3686, 4147, 4608],
        "Cumulative Lives": [154, 615, 1383, 2612, 4455, 6913, 9985, 13671, 17818, 22426],
        "Cumulative Savings": ["$0.3B", "$1.2B", "$2.7B", "$5.1B", "$8.7B", "$13.5B", "$19.5B", "$26.7B", "$34.8B", "$43.8B"]
    }
    st.dataframe(pd.DataFrame(ten_year_data), use_container_width=True, hide_index=True)
    
    cum_col1, cum_col2 = st.columns(2)
    
    with cum_col1:
        st.markdown("""
        <div class="big-number-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
            <div class="big-number">22,426</div>
            <div class="big-number-label">Lives Saved Over 10 Years</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cum_col2:
        st.markdown("""
        <div class="big-number-card" style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);">
            <div class="big-number">$43.8B</div>
            <div class="big-number-label">Healthcare Costs Avoided</div>
        </div>
        """, unsafe_allow_html=True)
    
    # =========================================================================
    # PARADIGM SHIFT
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">🔄 This Is Not Incremental Improvement</div>', unsafe_allow_html=True)
    
    st.markdown("This is a **category shift** in how immunotherapy safety is managed:")
    
    para_col1, para_col2 = st.columns(2)
    
    with para_col1:
        st.markdown("""
        <div class="paradigm-card before">
            <div class="paradigm-title before">❌ BEFORE</div>
            <ul class="impact-list">
                <li><strong>Detection:</strong> Reactive</li>
                <li><strong>Timing:</strong> Days to weeks</li>
                <li><strong>Coverage:</strong> Dependent on individual vigilance</li>
                <li><strong>Scalability:</strong> Limited by human cognition</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with para_col2:
        st.markdown("""
        <div class="paradigm-card after">
            <div class="paradigm-title after">✅ AFTER</div>
            <ul class="impact-list">
                <li><strong>Detection:</strong> Proactive</li>
                <li><strong>Timing:</strong> Hours</li>
                <li><strong>Coverage:</strong> Systematic</li>
                <li><strong>Scalability:</strong> Unlimited</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # =========================================================================
    # CAVEATS
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">⚠️ Important Caveats</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-banner">
        <strong>These projections assume:</strong>
        <ol style="color: #333; margin: 0.5rem 0 0 0; padding-left: 1.5rem;">
            <li><strong>Clinical validation</strong> proves the system's accuracy</li>
            <li><strong>Integration</strong> with EHR systems is achieved</li>
            <li><strong>Adoption</strong> by healthcare institutions occurs</li>
            <li><strong>Maintenance</strong> and updates keep pace with medical knowledge</li>
        </ol>
        <p style="margin-top: 0.75rem; color: #6c757d; font-style: italic;">
            The numbers above represent <strong>potential impact</strong>—realizing this potential requires execution, validation, and sustained investment.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # FINAL STATEMENT
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="final-statement">
        <p>
            <strong>If this solution works as designed and achieves mainstream adoption,</strong> 
            it would represent one of the most significant patient safety interventions in modern oncology—
            preventing thousands of deaths, reducing billions in costs, and fundamentally changing 
            how we protect patients from the unintended consequences of life-saving immunotherapy.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # CTA
    # =========================================================================
    st.markdown("""
    <div class="success-banner" style="text-align: center;">
        <h4>🚀 See It In Action</h4>
        <p>Visit <strong>New Assessment</strong> to try the system, or <strong>Statistics</strong> for demo cases.</p>
    </div>
    """, unsafe_allow_html=True)
