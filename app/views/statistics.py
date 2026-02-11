"""
Statistics and Insights View

Comprehensive visualization of irAE epidemiology, mortality rates,
and clinical impact to demonstrate the importance of early detection.
"""

import streamlit as st


def render():
    """Render the statistics and insights page."""
    
    st.markdown('<p class="main-header">📈 irAE Statistics & Clinical Impact</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Understanding why early detection matters</p>', unsafe_allow_html=True)
    
    # =========================================================================
    # KEY STATISTICS HERO SECTION
    # =========================================================================
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Patients Affected",
            value="44%",
            delta="of immunotherapy patients",
            delta_color="off"
        )
    
    with col2:
        st.metric(
            label="Cardiac Mortality",
            value="25-50%",
            delta="if myocarditis missed",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="Detection Window",
            value="48 hrs",
            delta="Grade 2 → Grade 4",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="Early Detection",
            value="80%+",
            delta="survival with prompt treatment",
            delta_color="normal"
        )
    
    st.markdown("---")
    
    # =========================================================================
    # INCIDENCE BY ORGAN SYSTEM
    # =========================================================================
    st.subheader("🫀 irAE Incidence by Organ System")
    
    st.markdown("""
    Immune checkpoint inhibitors can affect virtually any organ system. 
    The frequency varies by drug class and combination therapy.
    """)
    
    # Create two columns for the chart and details
    col_chart, col_details = st.columns([2, 1])
    
    with col_chart:
        # Incidence data
        organ_data = {
            "Organ System": [
                "Skin (Dermatitis)",
                "Gastrointestinal (Colitis)",
                "Hepatic (Hepatitis)",
                "Endocrine (Thyroiditis)",
                "Pulmonary (Pneumonitis)",
                "Renal (Nephritis)",
                "Neurologic",
                "Cardiac (Myocarditis)",
                "Hematologic"
            ],
            "Monotherapy (%)": [30, 15, 5, 10, 3, 2, 1, 0.5, 1],
            "Combination (%)": [50, 35, 15, 20, 10, 5, 3, 1.5, 3],
        }
        
        import pandas as pd
        df = pd.DataFrame(organ_data)
        
        st.bar_chart(
            df.set_index("Organ System")[["Monotherapy (%)", "Combination (%)"]],
            use_container_width=True
        )
    
    with col_details:
        st.markdown("""
        **Key Insights:**
        
        🔴 **Combination therapy** (ipilimumab + nivolumab) 
        has **2-3x higher** irAE rates
        
        ⚠️ **Skin and GI** are most common 
        but often manageable
        
        💔 **Cardiac and Neuro** are rare 
        but have highest mortality
        
        📊 **Early detection** dramatically 
        improves outcomes across all systems
        """)
    
    st.markdown("---")
    
    # =========================================================================
    # MORTALITY BY ORGAN SYSTEM
    # =========================================================================
    st.subheader("☠️ Mortality Risk by irAE Type")
    
    st.error("""
    **Critical Safety Information:** Some irAEs have extremely high mortality rates if not detected early.
    This is why our system enforces minimum urgency levels that cannot be overridden.
    """)
    
    # Mortality table
    mortality_data = {
        "irAE Type": [
            "Myocarditis (Cardiac)",
            "Myasthenia Gravis (Neuro)",
            "Encephalitis (Neuro)",
            "Severe Pneumonitis",
            "Fulminant Hepatitis",
            "Severe Colitis",
            "Adrenal Crisis",
            "Stevens-Johnson Syndrome"
        ],
        "Mortality Rate": [
            "25-50%",
            "10-20%",
            "10-15%",
            "10-15%",
            "5-10%",
            "2-5%",
            "5-10% (if untreated)",
            "10-30%"
        ],
        "Time to Crisis": [
            "Hours to days",
            "Days",
            "Days",
            "Days to weeks",
            "Days",
            "Days to weeks",
            "Hours",
            "Days"
        ],
        "System Response": [
            "🔴 ALWAYS EMERGENCY",
            "🔴 ALWAYS URGENT",
            "🔴 ALWAYS EMERGENCY",
            "🟠 Grade 3+ = URGENT",
            "🟠 Grade 3+ = URGENT",
            "🟠 Grade 3+ = URGENT",
            "🔴 ALWAYS URGENT",
            "🔴 ALWAYS EMERGENCY"
        ]
    }
    
    import pandas as pd
    mortality_df = pd.DataFrame(mortality_data)
    
    st.dataframe(
        mortality_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "irAE Type": st.column_config.TextColumn("irAE Type", width="medium"),
            "Mortality Rate": st.column_config.TextColumn("Mortality Rate", width="small"),
            "Time to Crisis": st.column_config.TextColumn("Time to Crisis", width="small"),
            "System Response": st.column_config.TextColumn("Our System Response", width="medium"),
        }
    )
    
    st.markdown("---")
    
    # =========================================================================
    # CTCAE GRADING VISUAL
    # =========================================================================
    st.subheader("📊 CTCAE Severity Grading System")
    
    st.markdown("""
    Our system uses the **Common Terminology Criteria for Adverse Events (CTCAE)** v5.0,
    the gold standard for oncology toxicity grading used in clinical trials and practice.
    """)
    
    grade_col1, grade_col2 = st.columns(2)
    
    with grade_col1:
        st.success("""
        **🟢 Grade 1 - Mild**
        - Asymptomatic or mild symptoms
        - Clinical observation only
        - No intervention required
        - *Example: Mild rash, 2-3 stools/day*
        
        **→ Urgency: ROUTINE** (next scheduled visit)
        """)
        
        st.warning("""
        **🟡 Grade 2 - Moderate**
        - Symptomatic, limiting daily activities
        - Minimal/local intervention indicated
        - May require treatment modification
        - *Example: 4-6 stools/day, AST 3-5x ULN*
        
        **→ Urgency: SOON** (oncology review 1-3 days)
        """)
    
    with grade_col2:
        st.error("""
        **🟠 Grade 3 - Severe**
        - Severe symptoms, hospitalization indicated
        - Disabling, limits self-care
        - IV intervention needed
        - *Example: ≥7 stools/day, AST >5x ULN*
        
        **→ Urgency: URGENT** (same-day evaluation)
        """)
        
        st.markdown("""
        <div style="background-color: #880000; color: white; padding: 1rem; border-radius: 5px;">
        <strong>🔴 Grade 4 - Life-Threatening</strong><br><br>
        • Life-threatening consequences<br>
        • Urgent intervention required<br>
        • ICU-level care may be needed<br>
        • <em>Example: Respiratory failure, cardiac arrest</em><br><br>
        <strong>→ Urgency: EMERGENCY</strong> (immediate/ER)
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # =========================================================================
    # TIMELINE: WHY EARLY DETECTION MATTERS
    # =========================================================================
    st.subheader("⏱️ The Critical Window: Why Hours Matter")
    
    st.info("""
    **Case Study: Grade 2 Colitis Progression**
    
    This timeline shows how a manageable irAE can become life-threatening without early detection.
    """)
    
    timeline_col1, timeline_col2, timeline_col3, timeline_col4 = st.columns(4)
    
    with timeline_col1:
        st.markdown("""
        ### Day 1
        **Grade 2 Colitis**
        
        🟡 5-6 loose stools/day
        
        *If detected:*
        - Hold immunotherapy
        - Start oral steroids
        - 90% resolve with treatment
        """)
    
    with timeline_col2:
        st.markdown("""
        ### Day 2-3
        **Progressing**
        
        🟠 Worsening diarrhea
        
        *If still missed:*
        - Inflammation spreading
        - Risk of perforation rising
        - Now needs IV steroids
        """)
    
    with timeline_col3:
        st.markdown("""
        ### Day 4-5
        **Grade 3-4**
        
        🔴 Bloody diarrhea, fever
        
        *Consequences:*
        - Hospitalization required
        - IV methylprednisolone
        - May need biologics
        """)
    
    with timeline_col4:
        st.markdown("""
        ### Day 5+
        **Complications**
        
        ☠️ Perforation risk
        
        *Worst case:*
        - Emergency surgery
        - ICU admission
        - 2-5% mortality
        """)
    
    st.markdown("---")
    
    # =========================================================================
    # CHECKPOINT INHIBITOR COMPARISON
    # =========================================================================
    st.subheader("💊 Checkpoint Inhibitor Risk Profiles")
    
    st.markdown("""
    Different checkpoint inhibitors have different irAE profiles. 
    **Combination therapy carries the highest risk** but also often has the best efficacy.
    """)
    
    drug_data = {
        "Drug Class": ["PD-1 Inhibitors", "PD-L1 Inhibitors", "CTLA-4 Inhibitors", "Combination (PD-1 + CTLA-4)"],
        "Examples": [
            "Pembrolizumab, Nivolumab",
            "Atezolizumab, Durvalumab",
            "Ipilimumab",
            "Ipi + Nivo"
        ],
        "Any Grade irAE": ["60-70%", "50-60%", "70-80%", "90-95%"],
        "Grade 3-4 irAE": ["10-20%", "10-15%", "20-30%", "40-60%"],
        "Most Common": [
            "Thyroid, Pneumonitis",
            "Hepatitis, Rash",
            "Colitis, Hypophysitis",
            "All systems at risk"
        ]
    }
    
    import pandas as pd
    drug_df = pd.DataFrame(drug_data)
    
    st.dataframe(
        drug_df,
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # =========================================================================
    # THE SOLUTION: OUR SYSTEM
    # =========================================================================
    st.subheader("🛡️ How Our System Addresses These Challenges")
    
    solution_col1, solution_col2, solution_col3 = st.columns(3)
    
    with solution_col1:
        st.markdown("""
        ### 🔍 DETECT
        
        **Multi-source analysis:**
        - Clinical notes (NLP)
        - Lab values (rule-based)
        - Medications (ICI detection)
        - Symptoms (pattern matching)
        
        **9 organ systems** monitored simultaneously
        """)
    
    with solution_col2:
        st.markdown("""
        ### 📊 GRADE
        
        **CTCAE-compliant grading:**
        - Threshold-based lab grading
        - Symptom severity scoring
        - Multi-factor assessment
        
        **MedGemma AI** provides clinical reasoning
        """)
    
    with solution_col3:
        st.markdown("""
        ### 🚨 TRIAGE
        
        **Safety-first urgency:**
        - Grade 2+ = NEVER routine
        - Cardiac = ALWAYS emergency
        - Neuro = ALWAYS urgent
        
        **SafetyValidator** enforces floors
        """)
    
    st.markdown("---")
    
    # =========================================================================
    # REFERENCES
    # =========================================================================
    with st.expander("📚 Data Sources & References"):
        st.markdown("""
        **Clinical Guidelines:**
        - NCCN Guidelines: Management of Immunotherapy-Related Toxicities
        - ASCO/SITC Clinical Practice Guideline on Management of Immune-Related Adverse Events
        - ESMO Clinical Practice Guidelines on irAE Management
        
        **Key Publications:**
        - Wang DY et al. Fatal Toxic Effects Associated With Immune Checkpoint Inhibitors. *JAMA Oncol.* 2018
        - Postow MA et al. Immune-Related Adverse Events Associated with Immune Checkpoint Blockade. *NEJM* 2018
        - Brahmer JR et al. Society for Immunotherapy of Cancer (SITC) Toxicity Management Guidelines
        
        **Incidence Data:**
        - Combination therapy irAE rates: Larkin J et al. *NEJM* 2015 (CheckMate 067)
        - Cardiac mortality: Mahmood SS et al. *JACC* 2018
        - Overall irAE incidence: Meta-analyses from multiple trials
        
        **CTCAE Grading:**
        - Common Terminology Criteria for Adverse Events (CTCAE) Version 5.0, NCI
        """)
    
    # =========================================================================
    # CALL TO ACTION
    # =========================================================================
    st.markdown("---")
    
    st.success("""
    ### Ready to See It In Action?
    
    Try our system with real clinical scenarios in the **🧪 Sample Cases** section,
    or enter your own patient data in **📋 New Assessment**.
    """)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn2:
        if st.button("🧪 Try Sample Cases", use_container_width=True):
            st.session_state.nav_to = "sample_cases"
            st.rerun()
