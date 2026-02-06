"""Sample Cases page with categorized clinical scenarios for demonstration."""

import streamlit as st
import asyncio
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.patient import PatientData
from src.parsers import LabParser, MedicationParser, SymptomParser
from src.llm.assessment_engine import IRAEAssessmentEngine


# =============================================================================
# Sample Clinical Cases by Category
# =============================================================================

SAMPLE_CASES = {
    "🔴 Gastrointestinal (Colitis)": {
        "Grade 2 - Moderate Colitis": {
            "description": "58-year-old male on pembrolizumab for melanoma with diarrhea",
            "patient_id": "GI-001",
            "age": 58,
            "cancer_type": "Melanoma",
            "medications": """Pembrolizumab 200mg IV q3weeks
Ondansetron 8mg PRN
Lisinopril 10mg daily""",
            "labs": """WBC: 11.2 x10^9/L (H)
CRP: 2.8 mg/dL (H)
Albumin: 3.2 g/dL (L)
Hemoglobin: 12.5 g/dL""",
            "symptoms": """Diarrhea - 5-6 loose stools daily for 4 days
Abdominal cramping - mild
No blood in stool
No fever""",
            "notes": """Patient on cycle 4 of pembrolizumab for stage IIIC melanoma.
Reports onset of loose stools 4 days ago, now having 5-6 episodes daily.
Mild periumbilical cramping. No mucus or blood. Appetite slightly decreased.
No recent antibiotic use. No sick contacts."""
        },
        "Grade 3 - Severe Colitis": {
            "description": "65-year-old female on nivolumab with severe diarrhea and bloody stools",
            "patient_id": "GI-002",
            "age": 65,
            "cancer_type": "Non-small cell lung cancer",
            "medications": """Nivolumab 480mg IV q4weeks
Prednisone 10mg daily (started 2 days ago)
Loperamide 2mg PRN""",
            "labs": """WBC: 14.5 x10^9/L (H)
CRP: 8.5 mg/dL (H)
Albumin: 2.8 g/dL (L)
Potassium: 3.2 mEq/L (L)
Creatinine: 1.4 mg/dL (H)""",
            "symptoms": """Diarrhea - 8-10 watery stools daily
Blood in stool - present
Severe abdominal pain
Fever - 38.2°C
Dehydration signs""",
            "notes": """Patient on nivolumab for metastatic NSCLC.
Severe watery diarrhea started 1 week ago, now with visible blood.
Diffuse abdominal tenderness on exam. Signs of dehydration.
Started low-dose prednisone 2 days ago without improvement."""
        },
    },
    "🟠 Hepatotoxicity": {
        "Grade 2 - Moderate Hepatitis": {
            "description": "52-year-old male on atezolizumab with elevated liver enzymes",
            "patient_id": "HEP-001",
            "age": 52,
            "cancer_type": "Urothelial carcinoma",
            "medications": """Atezolizumab 1200mg IV q3weeks
Metformin 1000mg BID
Omeprazole 20mg daily""",
            "labs": """AST: 156 U/L (H) - baseline 28
ALT: 189 U/L (H) - baseline 32
ALP: 145 U/L (H)
Total Bilirubin: 1.8 mg/dL (H)
INR: 1.1""",
            "symptoms": """Fatigue - moderate
Mild nausea
No jaundice
No abdominal pain""",
            "notes": """Routine labs show AST/ALT elevation >3x ULN.
Patient asymptomatic except for mild fatigue.
No alcohol use. No new medications.
Viral hepatitis panel pending."""
        },
        "Grade 3 - Severe Hepatitis": {
            "description": "48-year-old female on ipilimumab/nivolumab with severe hepatitis",
            "patient_id": "HEP-002",
            "age": 48,
            "cancer_type": "Melanoma",
            "medications": """Ipilimumab 3mg/kg + Nivolumab 1mg/kg IV q3weeks
Acetaminophen 500mg PRN""",
            "labs": """AST: 485 U/L (H)
ALT: 612 U/L (H)
ALP: 210 U/L (H)
Total Bilirubin: 3.2 mg/dL (H)
Direct Bilirubin: 2.1 mg/dL (H)
INR: 1.4 (H)
Albumin: 3.0 g/dL (L)""",
            "symptoms": """Jaundice - visible scleral icterus
Fatigue - severe
Nausea and anorexia
Dark urine
Right upper quadrant discomfort""",
            "notes": """Patient on combination immunotherapy for metastatic melanoma.
Developed jaundice over past week. AST/ALT >10x ULN.
Hepatitis panel negative. No hepatotoxic medications.
Ultrasound shows no biliary obstruction."""
        },
    },
    "🔵 Pneumonitis": {
        "Grade 2 - Moderate Pneumonitis": {
            "description": "67-year-old male on durvalumab with new cough and dyspnea",
            "patient_id": "LUNG-001",
            "age": 67,
            "cancer_type": "Non-small cell lung cancer",
            "medications": """Durvalumab 10mg/kg IV q2weeks
Albuterol inhaler PRN
Lisinopril 20mg daily""",
            "labs": """WBC: 9.8 x10^9/L
LDH: 280 U/L (H)
CRP: 3.2 mg/dL (H)
Procalcitonin: 0.15 ng/mL""",
            "symptoms": """Dry cough - new onset, 2 weeks
Dyspnea on exertion - moderate
No fever
O2 saturation: 94% on room air""",
            "notes": """Post-chemoradiation consolidation durvalumab.
New dry cough and exertional dyspnea x 2 weeks.
CT chest shows new bilateral ground-glass opacities.
No infectious symptoms. Sputum culture negative."""
        },
        "Grade 3 - Severe Pneumonitis": {
            "description": "71-year-old female with severe respiratory distress on pembrolizumab",
            "patient_id": "LUNG-002",
            "age": 71,
            "cancer_type": "Non-small cell lung cancer",
            "medications": """Pembrolizumab 200mg IV q3weeks
Oxygen 4L NC
Azithromycin 500mg daily (started empirically)""",
            "labs": """WBC: 11.5 x10^9/L
LDH: 450 U/L (H)
CRP: 12.5 mg/dL (H)
PaO2: 58 mmHg on 4L NC
Procalcitonin: 0.2 ng/mL""",
            "symptoms": """Severe dyspnea at rest
Persistent dry cough
Hypoxia requiring supplemental O2
Tachypnea - RR 28
No fever""",
            "notes": """Patient on pembrolizumab for stage IV NSCLC.
Progressive dyspnea over 1 week, now requiring 4L O2.
CT shows extensive bilateral GGO and consolidation.
BAL cultures negative. Considering ICU transfer."""
        },
    },
    "🟡 Endocrine": {
        "Hypothyroidism": {
            "description": "55-year-old female on nivolumab with fatigue and weight gain",
            "patient_id": "ENDO-001",
            "age": 55,
            "cancer_type": "Renal cell carcinoma",
            "medications": """Nivolumab 240mg IV q2weeks
Amlodipine 5mg daily""",
            "labs": """TSH: 28.5 mIU/L (H) - baseline 2.1
Free T4: 0.4 ng/dL (L)
Free T3: 1.8 pg/mL (L)
Anti-TPO: positive""",
            "symptoms": """Fatigue - progressive over 4 weeks
Weight gain - 8 lbs in 1 month
Cold intolerance
Constipation
Dry skin""",
            "notes": """Patient on nivolumab for metastatic RCC.
Progressive fatigue and weight gain over past month.
TSH markedly elevated with low free T4.
Classic hypothyroid symptoms present."""
        },
        "Hypophysitis": {
            "description": "62-year-old male on ipilimumab with headache and fatigue",
            "patient_id": "ENDO-002",
            "age": 62,
            "cancer_type": "Melanoma",
            "medications": """Ipilimumab 3mg/kg IV q3weeks (4th dose)
Hydrochlorothiazide 25mg daily""",
            "labs": """ACTH: 5 pg/mL (L)
Cortisol (AM): 2.1 ug/dL (L)
TSH: 0.5 mIU/L (L)
Free T4: 0.6 ng/dL (L)
LH: 1.2 mIU/mL (L)
FSH: 2.0 mIU/mL (L)
Testosterone: 85 ng/dL (L)
Prolactin: 45 ng/mL (H)""",
            "symptoms": """Severe headache - frontal
Profound fatigue
Nausea
Visual disturbance - none
Dizziness on standing""",
            "notes": """Patient after 4th dose of ipilimumab for melanoma.
New severe headache and fatigue over past week.
Labs show panhypopituitarism pattern.
MRI pituitary shows enlarged gland with heterogeneous enhancement."""
        },
    },
    "🟣 Dermatologic": {
        "Grade 2 - Maculopapular Rash": {
            "description": "45-year-old female on pembrolizumab with widespread rash",
            "patient_id": "SKIN-001",
            "age": 45,
            "cancer_type": "Triple-negative breast cancer",
            "medications": """Pembrolizumab 200mg IV q3weeks
Diphenhydramine 25mg PRN
Hydrocortisone cream 1% topical""",
            "labs": """WBC: 8.5 x10^9/L
Eosinophils: 8% (H)
LFTs: normal
Creatinine: 0.9 mg/dL""",
            "symptoms": """Maculopapular rash - trunk and extremities
Pruritus - moderate
BSA involvement: ~35%
No mucosal involvement
No blistering""",
            "notes": """Patient on cycle 3 of pembrolizumab for TNBC.
Developed pruritic rash 10 days after last infusion.
Erythematous maculopapular eruption on trunk and arms.
No fever, no mucosal involvement, no bullae."""
        },
        "Grade 3 - Severe Bullous Dermatitis": {
            "description": "58-year-old male with severe skin reaction on combination therapy",
            "patient_id": "SKIN-002",
            "age": 58,
            "cancer_type": "Melanoma",
            "medications": """Ipilimumab + Nivolumab combination
Prednisone 40mg daily (started 3 days ago)
Triamcinolone ointment 0.1%""",
            "labs": """WBC: 12.0 x10^9/L
Eosinophils: 15% (H)
AST: 45 U/L
ALT: 52 U/L""",
            "symptoms": """Bullous eruption - widespread
Skin pain
BSA involvement: >50%
Oral mucosal erosions present
Fever - 38.5°C""",
            "notes": """Patient on combination ICI for melanoma.
Severe bullous dermatitis developed over 5 days.
Multiple tense bullae on trunk and extremities.
Oral erosions present. Dermatology consulted.
Concern for bullous pemphigoid vs SJS."""
        },
    },
    "⚫ Neurologic": {
        "Myasthenia Gravis": {
            "description": "68-year-old male on nivolumab with ptosis and weakness",
            "patient_id": "NEURO-001",
            "age": 68,
            "cancer_type": "Small cell lung cancer",
            "medications": """Nivolumab 240mg IV q2weeks
Pyridostigmine 60mg TID (started 2 days ago)""",
            "labs": """CK: 180 U/L
Acetylcholine receptor antibodies: positive
Anti-striated muscle antibodies: positive
Troponin: 0.08 ng/mL (slightly elevated)""",
            "symptoms": """Bilateral ptosis
Diplopia
Dysphagia - mild
Proximal muscle weakness
Fatigue worse with activity""",
            "notes": """Patient on nivolumab for extensive stage SCLC.
Developed ptosis and diplopia over 1 week.
Fatigable weakness on exam. Ice pack test positive.
AChR antibodies positive. Concerned for irAE MG.
Monitor for respiratory involvement."""
        },
        "Encephalitis": {
            "description": "54-year-old female with confusion and seizure on pembrolizumab",
            "patient_id": "NEURO-002",
            "age": 54,
            "cancer_type": "Non-small cell lung cancer",
            "medications": """Pembrolizumab 200mg IV q3weeks
Levetiracetam 1000mg BID (started after seizure)
Methylprednisolone 1g IV daily""",
            "labs": """CSF: WBC 45 (lymphocyte predominant)
CSF protein: 85 mg/dL (H)
CSF glucose: 55 mg/dL (normal)
MRI brain: bilateral medial temporal lobe hyperintensity""",
            "symptoms": """Confusion - acute onset
Memory impairment
Seizure - witnessed generalized tonic-clonic
Headache
Personality change""",
            "notes": """Patient on pembrolizumab for NSCLC.
Acute confusion and witnessed seizure 3 days ago.
MRI shows bilateral medial temporal lobe T2 hyperintensity.
LP shows lymphocytic pleocytosis. Autoimmune encephalitis workup sent.
Started high-dose steroids."""
        },
    },
    "❤️ Cardiac": {
        "Myocarditis": {
            "description": "61-year-old male on combination ICI with chest pain and dyspnea",
            "patient_id": "CARD-001",
            "age": 61,
            "cancer_type": "Melanoma",
            "medications": """Ipilimumab 3mg/kg + Nivolumab 1mg/kg IV q3weeks
Metoprolol 25mg BID
Lisinopril 10mg daily""",
            "labs": """Troponin I: 2.8 ng/mL (H)
CK-MB: 45 ng/mL (H)
BNP: 850 pg/mL (H)
CRP: 8.5 mg/dL (H)
CK: 1200 U/L (H)""",
            "symptoms": """Chest pain - substernal, worse with exertion
Dyspnea - progressive
Palpitations
Fatigue - severe
Orthopnea""",
            "notes": """Patient on combination ipilimumab/nivolumab for melanoma.
Chest pain and dyspnea started 5 days ago.
ECG shows diffuse ST changes and low voltage.
Echo shows EF 35% (baseline 60%). Troponin elevated.
Urgent cardiology consult for suspected ICI myocarditis."""
        },
    },
}


def render():
    """Render the sample cases page."""
    st.markdown("## 🧪 Sample Clinical Cases")
    st.markdown("""
    Select a sample case below to see the irAE detection system in action.
    Cases are categorized by organ system and CTCAE severity grade.
    """)
    
    st.info("💡 **Tip:** Click on any case to auto-populate the assessment form and analyze for irAEs.")
    
    # Initialize session state
    if "selected_case" not in st.session_state:
        st.session_state.selected_case = None
    if "case_result" not in st.session_state:
        st.session_state.case_result = None
    
    # Create tabs for categories
    categories = list(SAMPLE_CASES.keys())
    tabs = st.tabs(categories)
    
    for tab, category in zip(tabs, categories):
        with tab:
            cases = SAMPLE_CASES[category]
            
            for case_name, case_data in cases.items():
                with st.expander(f"**{case_name}** - {case_data['description']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Patient ID:** {case_data['patient_id']}")
                        st.markdown(f"**Age:** {case_data['age']} | **Cancer:** {case_data['cancer_type']}")
                        
                        st.markdown("---")
                        
                        # Show case details in columns
                        detail_col1, detail_col2 = st.columns(2)
                        
                        with detail_col1:
                            st.markdown("**📦 Medications:**")
                            st.code(case_data['medications'], language=None)
                            
                            st.markdown("**🔬 Labs:**")
                            st.code(case_data['labs'], language=None)
                        
                        with detail_col2:
                            st.markdown("**🩺 Symptoms:**")
                            st.code(case_data['symptoms'], language=None)
                            
                            st.markdown("**📝 Clinical Notes:**")
                            st.text_area(
                                "Notes",
                                case_data['notes'],
                                height=150,
                                disabled=True,
                                key=f"notes_{case_data['patient_id']}",
                                label_visibility="collapsed"
                            )
                    
                    with col2:
                        st.markdown("###")
                        if st.button(
                            "🔍 Analyze Case",
                            key=f"analyze_{case_data['patient_id']}",
                            type="primary",
                            use_container_width=True
                        ):
                            analyze_case(case_data)
    
    # Show results if a case has been analyzed
    if st.session_state.case_result:
        st.markdown("---")
        display_case_results()


def analyze_case(case_data: dict):
    """Analyze a sample case and store results."""
    with st.spinner("🔄 Analyzing clinical data for irAEs..."):
        try:
            # Parse medications
            med_parser = MedicationParser()
            medications = med_parser.parse_medication_list(case_data['medications'])
            
            # Parse labs
            lab_parser = LabParser()
            labs = lab_parser.parse(case_data['labs'])
            
            # Parse symptoms
            symptom_parser = SymptomParser()
            symptoms = symptom_parser.parse(case_data['symptoms'])
            
            # Create patient data
            patient_data = PatientData(
                patient_id=case_data['patient_id'],
                age=case_data['age'],
                cancer_type=case_data['cancer_type'],
                medications=medications,
                labs=labs,
                symptoms=symptoms,
                raw_notes=case_data['notes'],
                raw_medications=case_data['medications'],
                raw_labs=case_data['labs'],
                raw_symptoms=case_data['symptoms'],
            )
            
            # Run assessment (rule-based only for demo)
            engine = IRAEAssessmentEngine(llm_client=None, use_llm=False)
            
            # Handle async assess method
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(engine.assess(patient_data))
            finally:
                loop.close()
            
            # Store results
            st.session_state.selected_case = case_data
            st.session_state.case_result = result
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error analyzing case: {str(e)}")


def display_case_results():
    """Display the analysis results for the selected case."""
    result = st.session_state.case_result
    case = st.session_state.selected_case
    
    st.markdown("## 📊 Analysis Results")
    st.markdown(f"**Case:** {case['patient_id']} - {case['description']}")
    
    # Urgency banner - extract just the urgency level from the enum value
    urgency_value = result.urgency.value if result.urgency else "unknown"
    # Extract urgency level (e.g., "🟠 Urgent (same day)" -> "urgent")
    urgency_key = "routine"
    if "Emergency" in urgency_value:
        urgency_key = "emergency"
    elif "Urgent" in urgency_value:
        urgency_key = "urgent"
    elif "soon" in urgency_value.lower():
        urgency_key = "soon"
    
    urgency_colors = {
        "emergency": ("🚨", "#f44336", "#ffebee"),
        "urgent": ("⚠️", "#ff9800", "#fff3e0"),
        "soon": ("📋", "#ffeb3b", "#fffde7"),
        "routine": ("✅", "#4caf50", "#e8f5e9"),
    }
    icon, border_color, bg_color = urgency_colors.get(urgency_key, ("❓", "#9e9e9e", "#f5f5f5"))
    
    st.markdown(f"""
    <div style="background-color: {bg_color}; border-left: 5px solid {border_color}; 
                padding: 1rem; margin: 1rem 0; border-radius: 5px;">
        <h3 style="margin: 0;">{icon} {urgency_value}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        immuno_status = "✅ Detected" if (result.immunotherapy_context and result.immunotherapy_context.on_immunotherapy) else "❌ Not Found"
        st.metric("Immunotherapy", immuno_status)
    
    with col2:
        # Count affected systems (where detected=True)
        affected = [f for f in result.affected_systems if f.detected] if result.affected_systems else []
        st.metric("Organ Systems Affected", len(affected))
    
    with col3:
        severity = result.overall_severity.value if result.overall_severity else "Unknown"
        st.metric("Overall Severity", severity.split(" - ")[0] if " - " in severity else severity)
    
    with col4:
        likelihood = result.causality.likelihood.value if result.causality else "Unknown"
        st.metric("irAE Likelihood", likelihood)
    
    # Immunotherapy context
    if result.immunotherapy_context and result.immunotherapy_context.on_immunotherapy:
        st.markdown("### 💉 Immunotherapy Context")
        ctx = result.immunotherapy_context
        st.markdown(f"- **Agent(s):** {', '.join(ctx.agents) if ctx.agents else 'Unknown'}")
        st.markdown(f"- **Drug Class:** {', '.join(ctx.drug_classes) if ctx.drug_classes else 'Unknown'}")
        if ctx.combination_therapy:
            st.markdown("- **⚠️ Combination therapy** (higher irAE risk)")
    
    # Organ findings
    affected_systems = [f for f in result.affected_systems if f.detected] if result.affected_systems else []
    if affected_systems:
        st.markdown("### 🏥 Organ System Findings")
        
        for finding in affected_systems:
            severity_str = finding.severity.value if finding.severity else "Unknown"
            severity_emoji = {
                "Grade 1": "🟢", 
                "Grade 2": "🟡", 
                "Grade 3": "🟠", 
                "Grade 4": "🔴"
            }
            emoji = "⚪"
            for grade, em in severity_emoji.items():
                if grade in severity_str:
                    emoji = em
                    break
            
            with st.expander(f"{emoji} **{finding.system.value}** - {severity_str}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Severity:** {severity_str}")
                    if finding.confidence:
                        st.markdown(f"**Confidence:** {finding.confidence:.0%}")
                    if finding.findings:
                        st.markdown("**Findings:**")
                        for f in finding.findings[:5]:
                            st.markdown(f"- {f}")
                
                with col2:
                    if finding.evidence:
                        st.markdown("**Supporting Evidence:**")
                        for evidence in finding.evidence[:5]:
                            st.markdown(f"- {evidence}")
    
    # Recommendations
    if result.recommended_actions:
        st.markdown("### 📋 Recommended Actions")
        
        # Sort by priority (1 is highest)
        sorted_actions = sorted(result.recommended_actions, key=lambda a: a.priority)
        
        high_priority = [a for a in sorted_actions if a.priority <= 2]
        medium_priority = [a for a in sorted_actions if a.priority == 3]
        low_priority = [a for a in sorted_actions if a.priority >= 4]
        
        if high_priority:
            st.markdown("#### 🚨 High Priority")
            for action in high_priority:
                st.markdown(f"- **{action.action}**")
                if action.rationale:
                    st.markdown(f"  - *{action.rationale}*")
        
        if medium_priority:
            st.markdown("#### ⚠️ Medium Priority")
            for action in medium_priority:
                st.markdown(f"- **{action.action}**")
                if action.rationale:
                    st.markdown(f"  - *{action.rationale}*")
        
        if low_priority:
            st.markdown("#### 📊 Monitoring/Follow-up")
            for action in low_priority:
                st.markdown(f"- {action.action}")
    
    # Key evidence
    if result.key_evidence:
        st.markdown("### 🔍 Key Evidence")
        for evidence in result.key_evidence:
            st.markdown(f"- {evidence}")
    
    # Causality assessment
    if result.causality:
        st.markdown("### 🔬 Causality Assessment")
        st.markdown(f"**Likelihood:** {result.causality.likelihood.value}")
        st.markdown(f"**Reasoning:** {result.causality.reasoning}")
        if result.causality.supporting_factors:
            st.markdown("**Supporting Factors:**")
            for factor in result.causality.supporting_factors:
                st.markdown(f"- ✅ {factor}")
        if result.causality.against_factors:
            st.markdown("**Factors Against irAE:**")
            for factor in result.causality.against_factors:
                st.markdown(f"- ❌ {factor}")
        if result.causality.alternative_causes:
            st.markdown("**Alternative Causes to Consider:**")
            for cause in result.causality.alternative_causes:
                st.markdown(f"- {cause}")
    
    # Disclaimer
    st.markdown("---")
    st.warning("""
    ⚠️ **Clinical Decision Support Only**
    
    This analysis is for demonstration purposes. All findings must be verified by a qualified 
    healthcare provider. This tool does not replace clinical judgment.
    """)
    
    # Clear button
    if st.button("🔄 Clear Results", type="secondary"):
        st.session_state.case_result = None
        st.session_state.selected_case = None
        st.rerun()
