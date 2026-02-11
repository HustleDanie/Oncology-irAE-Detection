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
    # THE PROBLEM: MESSY CLINICAL DATA
    # =========================================================================
    st.subheader("🔴 THE PROBLEM: Scattered Clinical Data")
    
    st.error("""
    **Real clinical data is fragmented across multiple systems.**
    Oncologists have ~15 minutes per patient and must manually connect dots across labs, notes, vitals, and medications.
    Critical irAE signals get lost in the noise.
    """)
    
    # Show the messy data in multiple columns to simulate fragmentation
    messy_col1, messy_col2, messy_col3 = st.columns(3)
    
    with messy_col1:
        st.markdown("""
        <div style="background-color: #2d2d3a; padding: 1rem; border-radius: 8px; border-left: 4px solid #e74c3c; font-family: monospace; font-size: 0.85rem; color: #ffffff;">
        <strong style="color: #ff6b6b;">📋 CLINICAL NOTE (buried in text)</strong><br><br>
        <span style="color: #aaaaaa;">...patient reports increased fatigue x2 weeks.</span>
        <span style="color: #aaaaaa;">Appetite decreased. </span>
        <span style="background-color: #ff4444; color: #ffffff; padding: 2px 6px; border-radius: 3px; font-weight: bold;">Loose stools 5-6x/day x4 days</span>
        <span style="color: #aaaaaa;">, attributes to dietary changes. Denies blood in stool. Continue current regimen...</span>
        </div>
        """, unsafe_allow_html=True)
    
    with messy_col2:
        st.markdown("""
        <div style="background-color: #2d2d3a; padding: 1rem; border-radius: 8px; border-left: 4px solid #f39c12; font-family: monospace; font-size: 0.85rem; color: #ffffff;">
        <strong style="color: #ffa500;">🔬 LAB RESULTS (separate system)</strong><br><br>
        <span style="color: #cccccc;">WBC: 8.2 K/uL</span><br>
        <span style="color: #cccccc;">Hgb: 11.8 g/dL</span><br>
        <span style="background-color: #ff8c00; color: #ffffff; padding: 2px 6px; border-radius: 3px; font-weight: bold;">CRP: 4.8 mg/dL ↑</span><br>
        <span style="background-color: #ff8c00; color: #ffffff; padding: 2px 6px; border-radius: 3px; font-weight: bold;">ESR: 42 mm/hr ↑</span><br>
        <span style="color: #cccccc;">Albumin: 3.2 g/dL</span><br>
        <span style="color: #888888;">... 47 more results ...</span>
        </div>
        """, unsafe_allow_html=True)
    
    with messy_col3:
        st.markdown("""
        <div style="background-color: #2d2d3a; padding: 1rem; border-radius: 8px; border-left: 4px solid #3498db; font-family: monospace; font-size: 0.85rem; color: #ffffff;">
        <strong style="color: #5dade2;">💊 MEDICATION LIST (another system)</strong><br><br>
        <span style="background-color: #3498db; color: #ffffff; padding: 2px 6px; border-radius: 3px; font-weight: bold;">Pembrolizumab 200mg q3wks</span><br>
        <span style="color: #cccccc;">Metformin 1000mg BID</span><br>
        <span style="color: #cccccc;">Lisinopril 10mg daily</span><br>
        <span style="color: #cccccc;">Omeprazole 20mg daily</span><br>
        <span style="color: #cccccc;">Vitamin D 2000 IU daily</span><br>
        <span style="color: #888888;">Last infusion: 2 weeks ago</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # The invisible connection
    st.warning("""
    **🔗 The connection that's easy to miss:**
    
    Pembrolizumab (immunotherapy) + Diarrhea 5-6x/day + Elevated CRP/ESR = **Grade 2 Colitis Pattern**
    
    But these signals are in **3 different systems**. Without AI assistance, it's easy to miss until symptoms escalate.
    """)
    
    st.markdown("---")
    
    # =========================================================================
    # RAPID ESCALATION TIMELINE
    # =========================================================================
    st.subheader("⚡ Rapid Escalation: 48-Hour Window")
    
    st.markdown("""
    <div style="background-color: #2d2d2d; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
    <h4 style="color: #e74c3c; margin-top: 0;">⏰ This is why every hour matters</h4>
    <p>A Grade 2 irAE can escalate to Grade 4 <strong>within 48 hours</strong> if not detected and treated.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Visual timeline with arrows
    esc_col1, arrow1, esc_col2, arrow2, esc_col3, arrow3, esc_col4 = st.columns([2, 0.5, 2, 0.5, 2, 0.5, 2])
    
    with esc_col1:
        st.markdown("""
        <div style="background-color: #ffc107; color: black; padding: 1rem; border-radius: 10px; text-align: center; height: 180px;">
        <h3 style="margin: 0; color: black;">Hour 0</h3>
        <h4 style="color: black;">Grade 2</h4>
        <hr style="border-color: black;">
        <small>
        5-6 loose stools/day<br>
        Patient uncomfortable<br>
        <strong>DETECTABLE</strong>
        </small>
        </div>
        """, unsafe_allow_html=True)
    
    with arrow1:
        st.markdown("""
        <div style="display: flex; align-items: center; height: 180px; justify-content: center;">
        <span style="font-size: 2rem; color: #ff6b6b;">→</span>
        </div>
        """, unsafe_allow_html=True)
    
    with esc_col2:
        st.markdown("""
        <div style="background-color: #fd7e14; color: white; padding: 1rem; border-radius: 10px; text-align: center; height: 180px;">
        <h3 style="margin: 0;">Hour 12-24</h3>
        <h4>Grade 2-3</h4>
        <hr>
        <small>
        Worsening frequency<br>
        Abdominal cramping<br>
        <strong>NEEDS STEROIDS</strong>
        </small>
        </div>
        """, unsafe_allow_html=True)
    
    with arrow2:
        st.markdown("""
        <div style="display: flex; align-items: center; height: 180px; justify-content: center;">
        <span style="font-size: 2rem; color: #ff6b6b;">→</span>
        </div>
        """, unsafe_allow_html=True)
    
    with esc_col3:
        st.markdown("""
        <div style="background-color: #dc3545; color: white; padding: 1rem; border-radius: 10px; text-align: center; height: 180px;">
        <h3 style="margin: 0;">Hour 24-48</h3>
        <h4>Grade 3</h4>
        <hr>
        <small>
        7+ stools/day<br>
        Blood in stool, fever<br>
        <strong>HOSPITALIZATION</strong>
        </small>
        </div>
        """, unsafe_allow_html=True)
    
    with arrow3:
        st.markdown("""
        <div style="display: flex; align-items: center; height: 180px; justify-content: center;">
        <span style="font-size: 2rem; color: #ff6b6b;">→</span>
        </div>
        """, unsafe_allow_html=True)
    
    with esc_col4:
        st.markdown("""
        <div style="background-color: #880000; color: white; padding: 1rem; border-radius: 10px; text-align: center; height: 180px;">
        <h3 style="margin: 0;">Hour 48+</h3>
        <h4>Grade 4</h4>
        <hr>
        <small>
        Perforation risk<br>
        Hemodynamic instability<br>
        <strong>ICU / SURGERY</strong>
        </small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key message
    st.success("""
    **🎯 Our system catches it at Hour 0:**
    
    By analyzing clinical notes, labs, and medications together, we detect the Grade 2 pattern **before escalation**.
    The patient gets treatment on Day 1, not Day 5 in the ICU.
    """)
    
    st.markdown("---")
    
    # =========================================================================
    # DEMO CLINICAL CASES - COPY & PASTE READY
    # =========================================================================
    st.subheader("📋 Demo Clinical Cases (Copy & Paste)")
    
    st.info("""
    **For hackathon demo:** Copy any of these cases into the assessment tool. 
    Expected outcomes are shown so you know what MedGemma should predict.
    """)
    
    # Case 1: GI Colitis - Grade 2
    with st.expander("🟡 CASE 1: GI Colitis (Grade 2) - Classic Demo Case", expanded=True):
        case1_col1, case1_col2 = st.columns([2, 1])
        
        with case1_col1:
            st.markdown("**📝 Clinical Case (copy this):**")
            case1_text = """58-year-old male with metastatic melanoma on pembrolizumab (cycle 4, last infusion 2 weeks ago).

Chief Complaint: Diarrhea x4 days

HPI: Patient reports 5-6 loose, watery stools daily for the past 4 days. Mild abdominal cramping. No blood in stool. No fever. Appetite slightly decreased.

Medications: Pembrolizumab 200mg IV q3wks, metformin 1000mg BID, lisinopril 10mg daily

Labs: WBC 8.2, CRP 4.8 mg/dL (elevated), ESR 42 mm/hr (elevated), albumin 3.2

Vitals: T 98.6F, BP 128/78, HR 82"""
            
            st.code(case1_text, language=None)
            
        with case1_col2:
            st.markdown("**✅ Expected MedGemma Output:**")
            st.markdown("""
            <div style="background-color: #1e3a1e; padding: 1rem; border-radius: 8px; font-size: 0.9rem;">
            <strong>irAE Detected:</strong> YES<br>
            <strong>System:</strong> Gastrointestinal<br>
            <strong>Condition:</strong> Colitis<br>
            <strong>Severity:</strong> Grade 2<br>
            <strong>Urgency:</strong> SOON (1-3 days)<br><br>
            <strong>Key Recommendations:</strong><br>
            • Hold pembrolizumab<br>
            • Start oral prednisone 1mg/kg<br>
            • Stool studies to r/o infection<br>
            • Follow-up in 48-72 hours
            </div>
            """, unsafe_allow_html=True)
    
    # Case 2: Cardiac - Grade 3 EMERGENCY
    with st.expander("🔴 CASE 2: Cardiac Myocarditis (Grade 3) - EMERGENCY Demo"):
        case2_col1, case2_col2 = st.columns([2, 1])
        
        with case2_col1:
            st.markdown("**📝 Clinical Case (copy this):**")
            case2_text = """67-year-old female with NSCLC on nivolumab + ipilimumab (cycle 2, last infusion 10 days ago).

Chief Complaint: Chest pain and shortness of breath x2 days

HPI: Progressive dyspnea on exertion, now at rest. Substernal chest pressure. New fatigue and palpitations. Unable to climb one flight of stairs without stopping.

Medications: Nivolumab 240mg + Ipilimumab 1mg/kg IV q3wks, aspirin 81mg, atorvastatin 40mg

Labs: Troponin I 0.89 ng/mL (elevated, normal <0.04), BNP 580 pg/mL (elevated), CK-MB 12.4

ECG: New PR prolongation, diffuse ST changes

Vitals: T 99.1F, BP 102/68, HR 108, O2 sat 92% on RA"""
            
            st.code(case2_text, language=None)
            
        with case2_col2:
            st.markdown("**✅ Expected MedGemma Output:**")
            st.markdown("""
            <div style="background-color: #3a1e1e; padding: 1rem; border-radius: 8px; font-size: 0.9rem;">
            <strong>irAE Detected:</strong> YES<br>
            <strong>System:</strong> Cardiac<br>
            <strong>Condition:</strong> Myocarditis<br>
            <strong>Severity:</strong> Grade 3<br>
            <strong>Urgency:</strong> 🚨 EMERGENCY<br><br>
            <strong>Key Recommendations:</strong><br>
            • STOP immunotherapy immediately<br>
            • Admit to cardiac monitoring unit<br>
            • IV methylprednisolone 1g/day<br>
            • Urgent cardiology consult<br>
            • Consider cardiac MRI
            </div>
            """, unsafe_allow_html=True)
            st.error("⚠️ Cardiac irAEs are ALWAYS emergency - this is hardcoded in SafetyValidator!")
    
    # Case 3: Hepatitis - Grade 2
    with st.expander("🟡 CASE 3: Hepatitis (Grade 2) - Elevated LFTs"):
        case3_col1, case3_col2 = st.columns([2, 1])
        
        with case3_col1:
            st.markdown("**📝 Clinical Case (copy this):**")
            case3_text = """52-year-old male with renal cell carcinoma on pembrolizumab (cycle 6).

Chief Complaint: Routine labs show elevated liver enzymes

HPI: Patient feels well. No jaundice, no abdominal pain, no nausea. No alcohol use. No new medications or supplements.

Medications: Pembrolizumab 200mg IV q3wks, amlodipine 5mg daily

Labs (today): AST 168 U/L (normal <40), ALT 195 U/L (normal <41), ALP 98, Total bilirubin 1.1
Labs (3 weeks ago): AST 32, ALT 38, ALP 85, Total bilirubin 0.8

Vitals: T 98.2F, BP 132/82, HR 76"""
            
            st.code(case3_text, language=None)
            
        with case3_col2:
            st.markdown("**✅ Expected MedGemma Output:**")
            st.markdown("""
            <div style="background-color: #1e3a1e; padding: 1rem; border-radius: 8px; font-size: 0.9rem;">
            <strong>irAE Detected:</strong> YES<br>
            <strong>System:</strong> Hepatic<br>
            <strong>Condition:</strong> Hepatitis<br>
            <strong>Severity:</strong> Grade 2 (AST/ALT 3-5x ULN)<br>
            <strong>Urgency:</strong> SOON (1-3 days)<br><br>
            <strong>Key Recommendations:</strong><br>
            • Hold pembrolizumab<br>
            • Recheck LFTs in 3-5 days<br>
            • Rule out viral hepatitis<br>
            • Consider hepatology consult<br>
            • Start steroids if worsening
            </div>
            """, unsafe_allow_html=True)
    
    # Case 4: Pneumonitis - Grade 3
    with st.expander("🟠 CASE 4: Pneumonitis (Grade 3) - URGENT"):
        case4_col1, case4_col2 = st.columns([2, 1])
        
        with case4_col1:
            st.markdown("**📝 Clinical Case (copy this):**")
            case4_text = """71-year-old male with metastatic bladder cancer on atezolizumab (cycle 5, last infusion 3 weeks ago).

Chief Complaint: Progressive shortness of breath x1 week

HPI: Worsening dyspnea, now requiring oxygen at home. Dry, nonproductive cough x10 days. Unable to perform daily activities. Denies fever, chills. No leg swelling.

Medications: Atezolizumab 1200mg IV q3wks, metoprolol 25mg BID, omeprazole 20mg

Labs: WBC 11.2, CRP 8.4 mg/dL (elevated)

Imaging: CT chest shows new bilateral ground-glass opacities, no PE

Vitals: T 98.8F, BP 138/84, HR 96, RR 24, O2 sat 88% on room air (94% on 3L NC)"""
            
            st.code(case4_text, language=None)
            
        with case4_col2:
            st.markdown("**✅ Expected MedGemma Output:**")
            st.markdown("""
            <div style="background-color: #3a2a1e; padding: 1rem; border-radius: 8px; font-size: 0.9rem;">
            <strong>irAE Detected:</strong> YES<br>
            <strong>System:</strong> Pulmonary<br>
            <strong>Condition:</strong> Pneumonitis<br>
            <strong>Severity:</strong> Grade 3 (O2 required)<br>
            <strong>Urgency:</strong> URGENT (same-day)<br><br>
            <strong>Key Recommendations:</strong><br>
            • STOP atezolizumab<br>
            • Admit for IV steroids<br>
            • IV methylprednisolone 2mg/kg<br>
            • Pulmonology consult<br>
            • Rule out infection (bronch if needed)
            </div>
            """, unsafe_allow_html=True)
    
    # Case 5: Endocrine (Thyroiditis) - Grade 1
    with st.expander("🟢 CASE 5: Thyroiditis (Grade 1) - Routine Monitoring"):
        case5_col1, case5_col2 = st.columns([2, 1])
        
        with case5_col1:
            st.markdown("**📝 Clinical Case (copy this):**")
            case5_text = """45-year-old female with melanoma on pembrolizumab (cycle 8).

Chief Complaint: Routine lab monitoring

HPI: Patient feels well overall. Mild fatigue but attributes to work stress. No weight changes, no temperature intolerance, no palpitations. Good appetite.

Medications: Pembrolizumab 200mg IV q3wks, vitamin D 2000 IU daily

Labs: TSH 6.8 mIU/L (elevated, normal 0.4-4.0), Free T4 0.9 ng/dL (low-normal), Free T3 2.4
Prior TSH (2 months ago): 2.1 mIU/L

Vitals: T 98.4F, BP 118/72, HR 68"""
            
            st.code(case5_text, language=None)
            
        with case5_col2:
            st.markdown("**✅ Expected MedGemma Output:**")
            st.markdown("""
            <div style="background-color: #1e2a3a; padding: 1rem; border-radius: 8px; font-size: 0.9rem;">
            <strong>irAE Detected:</strong> YES<br>
            <strong>System:</strong> Endocrine<br>
            <strong>Condition:</strong> Thyroiditis/Hypothyroidism<br>
            <strong>Severity:</strong> Grade 1 (asymptomatic)<br>
            <strong>Urgency:</strong> ROUTINE<br><br>
            <strong>Key Recommendations:</strong><br>
            • Continue pembrolizumab<br>
            • Recheck TSH in 4-6 weeks<br>
            • Start levothyroxine if symptomatic<br>
            • Monitor for progression<br>
            • Endocrine consult if T4 drops
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick reference table
    st.markdown("### 📊 Quick Reference: Demo Cases Summary")
    
    demo_summary = {
        "Case": ["Case 1", "Case 2", "Case 3", "Case 4", "Case 5"],
        "irAE Type": ["GI Colitis", "Cardiac Myocarditis", "Hepatitis", "Pneumonitis", "Thyroiditis"],
        "Grade": ["Grade 2", "Grade 3", "Grade 2", "Grade 3", "Grade 1"],
        "Urgency": ["🟡 SOON", "🔴 EMERGENCY", "🟡 SOON", "🟠 URGENT", "🟢 ROUTINE"],
        "Key Finding": ["5-6 stools/day", "Troponin 0.89, ECG changes", "AST/ALT 4-5x ULN", "O2 sat 88%, GGO on CT", "TSH 6.8"],
        "Demo Purpose": ["Classic case", "Safety validator", "Lab-based detection", "Imaging + symptoms", "Mild case handling"]
    }
    
    import pandas as pd
    demo_df = pd.DataFrame(demo_summary)
    
    st.dataframe(
        demo_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Urgency": st.column_config.TextColumn("Urgency", width="small"),
        }
    )
    
    st.success("""
    **💡 Demo Tip:** Start with Case 1 (GI Colitis) - it's the most common and easiest to explain. 
    Then show Case 2 (Cardiac) to demonstrate the SafetyValidator enforcing emergency urgency.
    """)
    
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
