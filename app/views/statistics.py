"""
Statistics and Insights View

Comprehensive visualization of irAE epidemiology, mortality rates,
and clinical impact to demonstrate the importance of early detection.

Redesigned with professional UI/UX for hackathon presentation.
"""

import streamlit as st
import pandas as pd


def render():
    """Render the statistics and insights page."""
    
    # =========================================================================
    # CUSTOM CSS FOR PROFESSIONAL STYLING
    # =========================================================================
    st.markdown("""
    <style>
    /* Stat Cards */
    .stat-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }
    
    .stat-value.red { color: #e74c3c; }
    .stat-value.orange { color: #f39c12; }
    .stat-value.green { color: #27ae60; }
    .stat-value.blue { color: #3498db; }
    
    .stat-label {
        font-size: 0.95rem;
        color: #495057;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    .stat-sublabel {
        font-size: 0.8rem;
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
    
    /* Problem Banner */
    .problem-banner {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(238, 90, 90, 0.3);
    }
    
    .problem-banner h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.3rem;
    }
    
    .problem-banner p {
        margin: 0;
        opacity: 0.95;
        font-size: 1rem;
    }
    
    /* Clinical Data Cards - WHITE BACKGROUND */
    .clinical-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border-left: 5px solid;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.85rem;
        color: #333333;
        min-height: 200px;
    }
    
    .clinical-card.notes { border-color: #e74c3c; }
    .clinical-card.labs { border-color: #f39c12; }
    .clinical-card.meds { border-color: #3498db; }
    
    .clinical-card-header {
        font-weight: 700;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .clinical-card-header.notes { color: #c0392b; }
    .clinical-card-header.labs { color: #d68910; }
    .clinical-card-header.meds { color: #2874a6; }
    
    .highlight-red {
        background: #ffebee;
        color: #c62828;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 700;
        display: inline;
    }
    
    .highlight-orange {
        background: #fff3e0;
        color: #e65100;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 700;
        display: inline-block;
        margin: 2px 0;
    }
    
    .highlight-blue {
        background: #e3f2fd;
        color: #1565c0;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 4px;
    }
    
    .text-muted {
        color: #757575;
    }
    
    .text-normal {
        color: #333333;
    }
    
    /* Connection Banner */
    .connection-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .connection-banner h4 {
        margin: 0 0 0.75rem 0;
        font-size: 1.1rem;
    }
    
    .connection-formula {
        font-size: 1rem;
        background: rgba(255,255,255,0.2);
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
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
    
    /* Timeline Cards */
    .timeline-card {
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        color: white;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    .timeline-card.grade2 { background: linear-gradient(135deg, #ffc107 0%, #ffb300 100%); color: #333; }
    .timeline-card.grade23 { background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); }
    .timeline-card.grade3 { background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%); }
    .timeline-card.grade4 { background: linear-gradient(135deg, #b71c1c 0%, #880e4f 100%); }
    
    .timeline-time {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    
    .timeline-grade {
        font-size: 1.1rem;
        font-weight: 600;
        opacity: 0.9;
    }
    
    .timeline-symptoms {
        font-size: 0.85rem;
        opacity: 0.9;
        line-height: 1.4;
    }
    
    .timeline-action {
        font-weight: 700;
        font-size: 0.9rem;
        background: rgba(255,255,255,0.25);
        padding: 0.4rem 0.75rem;
        border-radius: 20px;
    }
    
    .timeline-arrow {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        color: #e74c3c;
        min-height: 200px;
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
    
    /* Grade Cards - WHITE BACKGROUND */
    .grade-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.25rem;
        min-height: 180px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border: 2px solid;
    }
    
    .grade-card.grade1 { border-color: #28a745; }
    .grade-card.grade2 { border-color: #ffc107; }
    .grade-card.grade3 { border-color: #fd7e14; }
    .grade-card.grade4 { border-color: #dc3545; }
    
    .grade-title {
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .grade-title.g1 { color: #155724; }
    .grade-title.g2 { color: #856404; }
    .grade-title.g3 { color: #8a4500; }
    .grade-title.g4 { color: #721c24; }
    
    .grade-desc {
        font-size: 0.9rem;
        color: #495057;
        margin-bottom: 0.75rem;
    }
    
    .grade-urgency {
        font-weight: 700;
        padding: 0.4rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
        color: white;
    }
    
    .urgency-routine { background: #28a745; }
    .urgency-soon { background: #ffc107; color: #333; }
    .urgency-urgent { background: #fd7e14; }
    .urgency-emergency { background: #dc3545; }
    </style>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # HERO SECTION
    # =========================================================================
    st.markdown('<p class="main-header">📊 irAE Statistics & Clinical Impact</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Understanding why early detection saves lives</p>', unsafe_allow_html=True)
    
    # =========================================================================
    # KEY METRICS CARDS
    # =========================================================================
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value red">44%</div>
            <div class="stat-label">Patients Affected</div>
            <div class="stat-sublabel">of immunotherapy patients</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value orange">25-50%</div>
            <div class="stat-label">Cardiac Mortality</div>
            <div class="stat-sublabel">if myocarditis missed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value red">48 hrs</div>
            <div class="stat-label">Escalation Window</div>
            <div class="stat-sublabel">Grade 2 → Grade 4</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value green">80%+</div>
            <div class="stat-label">Survival Rate</div>
            <div class="stat-sublabel">with prompt treatment</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # =========================================================================
    # THE PROBLEM SECTION
    # =========================================================================
    st.markdown('<div class="section-header">🔴 The Problem: Fragmented Clinical Data</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="problem-banner">
        <h3>⚠️ Critical irAE signals get lost in the noise</h3>
        <p>Oncologists have ~15 minutes per patient and must manually connect dots across labs, notes, vitals, and medications stored in separate systems.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Clinical Data Cards - WHITE BACKGROUND, BLACK TEXT
    data_col1, data_col2, data_col3 = st.columns(3)
    
    with data_col1:
        st.markdown("""
        <div class="clinical-card notes">
            <div class="clinical-card-header notes">📋 CLINICAL NOTE</div>
            <span class="text-muted">...patient reports increased fatigue x2 weeks. Appetite decreased.</span>
            <span class="highlight-red">Loose stools 5-6x/day x4 days</span>
            <span class="text-muted">, attributes to dietary changes. Denies blood in stool. Continue current regimen...</span>
        </div>
        """, unsafe_allow_html=True)
    
    with data_col2:
        st.markdown("""
        <div class="clinical-card labs">
            <div class="clinical-card-header labs">🔬 LAB RESULTS</div>
            <span class="text-normal">WBC: 8.2 K/uL</span><br>
            <span class="text-normal">Hgb: 11.8 g/dL</span><br>
            <span class="highlight-orange">CRP: 4.8 mg/dL ↑</span><br>
            <span class="highlight-orange">ESR: 42 mm/hr ↑</span><br>
            <span class="text-normal">Albumin: 3.2 g/dL</span><br>
            <span class="text-muted">... 47 more results ...</span>
        </div>
        """, unsafe_allow_html=True)
    
    with data_col3:
        st.markdown("""
        <div class="clinical-card meds">
            <div class="clinical-card-header meds">💊 MEDICATIONS</div>
            <span class="highlight-blue">Pembrolizumab 200mg q3wks</span><br>
            <span class="text-normal">Metformin 1000mg BID</span><br>
            <span class="text-normal">Lisinopril 10mg daily</span><br>
            <span class="text-normal">Omeprazole 20mg daily</span><br>
            <span class="text-normal">Vitamin D 2000 IU daily</span><br>
            <span class="text-muted">Last infusion: 2 weeks ago</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="connection-banner">
        <h4>🔗 The Pattern Our AI Detects</h4>
        <div class="connection-formula">
            <strong>Pembrolizumab</strong> (ICI) + <strong>Diarrhea 5-6x/day</strong> + <strong>↑ CRP/ESR</strong> = <strong>Grade 2 Colitis</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # ESCALATION TIMELINE
    # =========================================================================
    st.markdown('<div class="section-header">⚡ Rapid Escalation: The 48-Hour Window</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>⏰ Why every hour matters:</strong> A Grade 2 irAE can progress to Grade 4 within 48 hours without proper intervention.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Timeline
    t_col1, t_arrow1, t_col2, t_arrow2, t_col3, t_arrow3, t_col4 = st.columns([2, 0.5, 2, 0.5, 2, 0.5, 2])
    
    with t_col1:
        st.markdown("""
        <div class="timeline-card grade2">
            <div>
                <div class="timeline-time">Hour 0</div>
                <div class="timeline-grade">Grade 2</div>
            </div>
            <div class="timeline-symptoms">
                5-6 loose stools/day<br>
                Patient uncomfortable
            </div>
            <div class="timeline-action">✓ DETECTABLE</div>
        </div>
        """, unsafe_allow_html=True)
    
    with t_arrow1:
        st.markdown('<div class="timeline-arrow">→</div>', unsafe_allow_html=True)
    
    with t_col2:
        st.markdown("""
        <div class="timeline-card grade23">
            <div>
                <div class="timeline-time">Hour 12-24</div>
                <div class="timeline-grade">Grade 2-3</div>
            </div>
            <div class="timeline-symptoms">
                Worsening frequency<br>
                Abdominal cramping
            </div>
            <div class="timeline-action">💊 NEEDS STEROIDS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with t_arrow2:
        st.markdown('<div class="timeline-arrow">→</div>', unsafe_allow_html=True)
    
    with t_col3:
        st.markdown("""
        <div class="timeline-card grade3">
            <div>
                <div class="timeline-time">Hour 24-48</div>
                <div class="timeline-grade">Grade 3</div>
            </div>
            <div class="timeline-symptoms">
                7+ stools/day<br>
                Blood in stool, fever
            </div>
            <div class="timeline-action">🏥 HOSPITALIZATION</div>
        </div>
        """, unsafe_allow_html=True)
    
    with t_arrow3:
        st.markdown('<div class="timeline-arrow">→</div>', unsafe_allow_html=True)
    
    with t_col4:
        st.markdown("""
        <div class="timeline-card grade4">
            <div>
                <div class="timeline-time">Hour 48+</div>
                <div class="timeline-grade">Grade 4</div>
            </div>
            <div class="timeline-symptoms">
                Perforation risk<br>
                Hemodynamic instability
            </div>
            <div class="timeline-action">🚨 ICU / SURGERY</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="success-banner">
        <h4>🎯 Our System Catches It at Hour 0</h4>
        <p>By analyzing clinical notes, labs, and medications together, we detect the Grade 2 pattern before escalation. The patient gets treatment on Day 1, not Day 5 in the ICU.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # DEMO CLINICAL CASES
    # =========================================================================
    st.markdown('<div class="section-header">📋 Demo Clinical Cases</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>💡 For hackathon demo:</strong> Copy each field into the corresponding input box in New Assessment → Free Text Input. Expected outputs show what MedGemma should predict.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Case 1: GI Colitis
    with st.expander("🟡 **CASE 1: GI Colitis** — Grade 2 • Urgency: SOON", expanded=True):
        c1_col1, c1_col2 = st.columns([3, 2])
        
        with c1_col1:
            st.markdown("**📝 Input Fields (copy into form):**")
            st.markdown("""
            | Field | Value |
            |-------|-------|
            | **Age** | 58 |
            | **Cancer Type** | Metastatic melanoma |
            | **☑ Immunotherapy** | ✓ Checked |
            """)
            
            st.markdown("**💊 Medications:**")
            st.code("Pembrolizumab 200mg IV q3wks\nMetformin 1000mg BID\nLisinopril 10mg daily", language=None)
            
            st.markdown("**🩺 Symptoms:**")
            st.code("Diarrhea - 5-6 loose watery stools daily\nAbdominal cramping - mild\nDecreased appetite", language=None)
            
            st.markdown("**🔬 Laboratory Results:**")
            st.code("WBC 8.2\nCRP 4.8 mg/dL (H)\nESR 42 mm/hr (H)\nAlbumin 3.2", language=None)
            
            st.markdown("**📋 Clinical Notes:**")
            st.code("58M on pembrolizumab cycle 4, last infusion 2 weeks ago. Diarrhea x4 days. No blood in stool. No fever. T 98.6F, BP 128/78, HR 82.", language=None)
        
        with c1_col2:
            st.markdown("**✅ Expected Output:**")
            st.markdown("""
            | Field | Value |
            |-------|-------|
            | **irAE Detected** | ✓ Yes |
            | **System** | Gastrointestinal |
            | **Condition** | Colitis |
            | **Grade** | Grade 2 |
            | **Urgency** | 🟡 SOON (1-3 days) |
            
            **Recommendations:**
            - Hold pembrolizumab
            - Start oral prednisone 1mg/kg
            - Stool studies to r/o infection
            - Follow-up in 48-72 hours
            """)
    
    # Case 2: Cardiac
    with st.expander("🔴 **CASE 2: Cardiac Myocarditis** — Grade 3 • Urgency: EMERGENCY"):
        c2_col1, c2_col2 = st.columns([3, 2])
        
        with c2_col1:
            st.markdown("**📝 Input Fields (copy into form):**")
            st.markdown("""
            | Field | Value |
            |-------|-------|
            | **Age** | 67 |
            | **Cancer Type** | Non-small cell lung cancer |
            | **☑ Immunotherapy** | ✓ Checked |
            """)
            
            st.markdown("**💊 Medications:**")
            st.code("Nivolumab 240mg IV q2wks\nIpilimumab 1mg/kg IV q6wks\nAspirin 81mg daily\nAtorvastatin 40mg daily", language=None)
            
            st.markdown("**🩺 Symptoms:**")
            st.code("Chest pain - substernal pressure x2 days\nShortness of breath - at rest\nFatigue - severe, new onset\nPalpitations", language=None)
            
            st.markdown("**🔬 Laboratory Results:**")
            st.code("Troponin I 0.89 ng/mL (H)\nBNP 580 pg/mL (H)\nCK-MB 12.4 (H)", language=None)
            
            st.markdown("**📋 Clinical Notes:**")
            st.code("67F NSCLC on nivo/ipi cycle 2, last infusion 10 days ago. Progressive dyspnea, chest pressure. ECG: new PR prolongation, diffuse ST changes. T 99.1F, BP 102/68, HR 108, O2 92% RA.", language=None)
        
        with c2_col2:
            st.markdown("**✅ Expected Output:**")
            st.markdown("""
            | Field | Value |
            |-------|-------|
            | **irAE Detected** | ✓ Yes |
            | **System** | Cardiac |
            | **Condition** | Myocarditis |
            | **Grade** | Grade 3 |
            | **Urgency** | 🔴 EMERGENCY |
            
            **Recommendations:**
            - STOP immunotherapy immediately
            - Admit to cardiac monitoring
            - IV methylprednisolone 1g/day
            - Urgent cardiology consult
            """)
            st.error("⚠️ Cardiac = ALWAYS EMERGENCY (SafetyValidator enforced)")
    
    # Case 3: Hepatitis
    with st.expander("🟡 **CASE 3: Hepatitis** — Grade 2 • Urgency: SOON"):
        c3_col1, c3_col2 = st.columns([3, 2])
        
        with c3_col1:
            st.markdown("**📝 Input Fields (copy into form):**")
            st.markdown("""
            | Field | Value |
            |-------|-------|
            | **Age** | 52 |
            | **Cancer Type** | Renal cell carcinoma |
            | **☑ Immunotherapy** | ✓ Checked |
            """)
            
            st.markdown("**💊 Medications:**")
            st.code("Pembrolizumab 200mg IV q3wks\nAmlodipine 5mg daily", language=None)
            
            st.markdown("**🩺 Symptoms:**")
            st.code("Asymptomatic\nNo jaundice\nNo abdominal pain\nNo nausea", language=None)
            
            st.markdown("**🔬 Laboratory Results:**")
            st.code("AST 168 U/L (H)\nALT 195 U/L (H)\nALP 98\nTotal bilirubin 1.1\nBaseline AST 32, ALT 38", language=None)
            
            st.markdown("**📋 Clinical Notes:**")
            st.code("52M RCC on pembrolizumab cycle 6. Routine labs show elevated LFTs. Patient feels well. No alcohol. No new meds. T 98.2F, BP 132/82, HR 76.", language=None)
        
        with c3_col2:
            st.markdown("**✅ Expected Output:**")
            st.markdown("""
            | Field | Value |
            |-------|-------|
            | **irAE Detected** | ✓ Yes |
            | **System** | Hepatic |
            | **Condition** | Hepatitis |
            | **Grade** | Grade 2 (3-5x ULN) |
            | **Urgency** | 🟡 SOON (1-3 days) |
            
            **Recommendations:**
            - Hold pembrolizumab
            - Recheck LFTs in 3-5 days
            - Rule out viral hepatitis
            - Start steroids if worsening
            """)
    
    # Case 4: Pneumonitis
    with st.expander("🟠 **CASE 4: Pneumonitis** — Grade 3 • Urgency: URGENT"):
        c4_col1, c4_col2 = st.columns([3, 2])
        
        with c4_col1:
            st.markdown("**📝 Input Fields (copy into form):**")
            st.markdown("""
            | Field | Value |
            |-------|-------|
            | **Age** | 71 |
            | **Cancer Type** | Metastatic bladder cancer |
            | **☑ Immunotherapy** | ✓ Checked |
            """)
            
            st.markdown("**💊 Medications:**")
            st.code("Atezolizumab 1200mg IV q3wks\nMetoprolol 25mg BID\nOmeprazole 20mg daily", language=None)
            
            st.markdown("**🩺 Symptoms:**")
            st.code("Shortness of breath - progressive x1 week\nDry cough x10 days\nUnable to perform daily activities\nRequiring home oxygen", language=None)
            
            st.markdown("**🔬 Laboratory Results:**")
            st.code("WBC 11.2\nCRP 8.4 mg/dL (H)\nO2 sat 88% on RA\nO2 sat 94% on 3L NC", language=None)
            
            st.markdown("**📋 Clinical Notes:**")
            st.code("71M bladder ca on atezolizumab cycle 5. Worsening dyspnea. CT chest: bilateral ground-glass opacities, no PE. T 98.8F, BP 138/84, HR 96, RR 24.", language=None)
        
        with c4_col2:
            st.markdown("**✅ Expected Output:**")
            st.markdown("""
            | Field | Value |
            |-------|-------|
            | **irAE Detected** | ✓ Yes |
            | **System** | Pulmonary |
            | **Condition** | Pneumonitis |
            | **Grade** | Grade 3 (O2 required) |
            | **Urgency** | 🟠 URGENT (same-day) |
            
            **Recommendations:**
            - STOP atezolizumab
            - Admit for IV steroids
            - Pulmonology consult
            - Rule out infection
            """)
    
    # Case 5: Thyroiditis
    with st.expander("🟢 **CASE 5: Thyroiditis** — Grade 1 • Urgency: ROUTINE"):
        c5_col1, c5_col2 = st.columns([3, 2])
        
        with c5_col1:
            st.markdown("**📝 Input Fields (copy into form):**")
            st.markdown("""
            | Field | Value |
            |-------|-------|
            | **Age** | 45 |
            | **Cancer Type** | Melanoma |
            | **☑ Immunotherapy** | ✓ Checked |
            """)
            
            st.markdown("**💊 Medications:**")
            st.code("Pembrolizumab 200mg IV q3wks\nVitamin D 2000 IU daily", language=None)
            
            st.markdown("**🩺 Symptoms:**")
            st.code("Fatigue - mild\nNo weight changes\nNo palpitations", language=None)
            
            st.markdown("**🔬 Laboratory Results:**")
            st.code("TSH 6.8 mIU/L (H)\nFree T4 0.9 ng/dL (low-normal)\nPrior TSH 2.1 mIU/L", language=None)
            
            st.markdown("**📋 Clinical Notes:**")
            st.code("45F melanoma on pembrolizumab cycle 8. Routine labs. Feels well, mild fatigue attributed to work. T 98.4F, BP 118/72, HR 68.", language=None)
        
        with c5_col2:
            st.markdown("**✅ Expected Output:**")
            st.markdown("""
            | Field | Value |
            |-------|-------|
            | **irAE Detected** | ✓ Yes |
            | **System** | Endocrine |
            | **Condition** | Thyroiditis |
            | **Grade** | Grade 1 (asymptomatic) |
            | **Urgency** | 🟢 ROUTINE |
            
            **Recommendations:**
            - Continue pembrolizumab
            - Recheck TSH in 4-6 weeks
            - Start levothyroxine if symptomatic
            - Monitor for progression
            """)
    
    # =========================================================================
    # QUICK REFERENCE TABLE
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Quick Reference: Demo Cases Summary")
    
    summary_data = {
        "Case": ["Case 1", "Case 2", "Case 3", "Case 4", "Case 5"],
        "irAE Type": ["GI Colitis", "Cardiac Myocarditis", "Hepatitis", "Pneumonitis", "Thyroiditis"],
        "Grade": ["Grade 2", "Grade 3", "Grade 2", "Grade 3", "Grade 1"],
        "Urgency": ["🟡 SOON", "🔴 EMERGENCY", "🟡 SOON", "🟠 URGENT", "🟢 ROUTINE"],
        "Key Finding": ["5-6 stools/day", "Troponin ↑, ECG Δ", "AST/ALT 4-5x", "O2 88%, GGO", "TSH 6.8"],
        "Demo Purpose": ["Classic case", "Safety validator", "Lab detection", "Imaging case", "Mild case"]
    }
    
    st.dataframe(
        pd.DataFrame(summary_data),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("""
    <div class="success-banner">
        <h4>💡 Demo Tip</h4>
        <p>Start with <strong>Case 1 (GI Colitis)</strong> — it's the most common and easiest to explain. Then show <strong>Case 2 (Cardiac)</strong> to demonstrate the SafetyValidator enforcing emergency urgency.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # CTCAE GRADING SYSTEM
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📊 CTCAE Severity Grading</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>Clinical Standard:</strong> Our system uses CTCAE v5.0 (Common Terminology Criteria for Adverse Events), the gold standard for oncology toxicity grading.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    g_col1, g_col2, g_col3, g_col4 = st.columns(4)
    
    with g_col1:
        st.markdown("""
        <div class="grade-card grade1">
            <div class="grade-title g1">🟢 Grade 1 — Mild</div>
            <div class="grade-desc">
                Asymptomatic or mild symptoms. Clinical observation only. No intervention required.
            </div>
            <div><span class="grade-urgency urgency-routine">ROUTINE</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with g_col2:
        st.markdown("""
        <div class="grade-card grade2">
            <div class="grade-title g2">🟡 Grade 2 — Moderate</div>
            <div class="grade-desc">
                Symptomatic, limiting daily activities. May require treatment modification.
            </div>
            <div><span class="grade-urgency urgency-soon">SOON (1-3 days)</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with g_col3:
        st.markdown("""
        <div class="grade-card grade3">
            <div class="grade-title g3">🟠 Grade 3 — Severe</div>
            <div class="grade-desc">
                Severe symptoms. Hospitalization indicated. IV intervention needed.
            </div>
            <div><span class="grade-urgency urgency-urgent">URGENT (same-day)</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with g_col4:
        st.markdown("""
        <div class="grade-card grade4">
            <div class="grade-title g4">🔴 Grade 4 — Life-Threatening</div>
            <div class="grade-desc">
                Life-threatening consequences. Urgent intervention required. ICU care.
            </div>
            <div><span class="grade-urgency urgency-emergency">EMERGENCY</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    # =========================================================================
    # INCIDENCE BY ORGAN SYSTEM
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">🫀 irAE Incidence by Organ System</div>', unsafe_allow_html=True)
    
    inc_col1, inc_col2 = st.columns([2, 1])
    
    with inc_col1:
        organ_data = {
            "Organ System": ["Skin", "GI (Colitis)", "Hepatic", "Endocrine", "Pulmonary", "Renal", "Neurologic", "Cardiac", "Hematologic"],
            "Monotherapy (%)": [30, 15, 5, 10, 3, 2, 1, 0.5, 1],
            "Combination (%)": [50, 35, 15, 20, 10, 5, 3, 1.5, 3],
        }
        df = pd.DataFrame(organ_data)
        st.bar_chart(df.set_index("Organ System"), use_container_width=True)
    
    with inc_col2:
        st.markdown("""
        **Key Insights:**
        
        🔴 **Combination therapy** has 2-3x higher irAE rates
        
        ⚠️ **Skin & GI** are most common but often manageable
        
        💔 **Cardiac & Neuro** are rare but have highest mortality
        
        📊 **Early detection** dramatically improves outcomes
        """)
    
    # =========================================================================
    # MORTALITY TABLE
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">☠️ Mortality Risk by irAE Type</div>', unsafe_allow_html=True)
    
    mortality_data = {
        "irAE Type": ["Myocarditis", "Myasthenia Gravis", "Encephalitis", "Severe Pneumonitis", "Fulminant Hepatitis", "Severe Colitis"],
        "Mortality Rate": ["25-50%", "10-20%", "10-15%", "10-15%", "5-10%", "2-5%"],
        "Time to Crisis": ["Hours-Days", "Days", "Days", "Days-Weeks", "Days", "Days-Weeks"],
        "System Response": ["🔴 EMERGENCY", "🔴 URGENT", "🔴 EMERGENCY", "🟠 Grade 3+ URGENT", "🟠 Grade 3+ URGENT", "🟠 Grade 3+ URGENT"]
    }
    
    st.dataframe(pd.DataFrame(mortality_data), use_container_width=True, hide_index=True)
    
    # =========================================================================
    # REFERENCES
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📚 Data Sources & References"):
        st.markdown("""
        **Clinical Guidelines:**
        - NCCN Guidelines: Management of Immunotherapy-Related Toxicities
        - ASCO/SITC Clinical Practice Guideline on Management of irAEs
        - ESMO Clinical Practice Guidelines
        
        **Key Publications:**
        - Wang DY et al. *JAMA Oncol.* 2018 — Fatal Toxic Effects with ICIs
        - Postow MA et al. *NEJM* 2018 — irAEs Associated with Checkpoint Blockade
        - Mahmood SS et al. *JACC* 2018 — Cardiac Mortality Data
        
        **Grading System:**
        - CTCAE v5.0, National Cancer Institute
        """)
    
    # =========================================================================
    # CTA
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="success-banner" style="text-align: center;">
        <h4>🚀 Ready to See It In Action?</h4>
        <p>Try our system with the sample cases above, or head to <strong>New Assessment</strong> to enter your own clinical data.</p>
    </div>
    """, unsafe_allow_html=True)
