"""Assessment page for entering patient clinical data."""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.patient import PatientData, LabResult, Medication, VitalSigns, PatientSymptom
from src.parsers import LabParser, MedicationParser, SymptomParser
from src.llm.assessment_engine import IRAEAssessmentEngine


def render():
    """Render the assessment page."""
    st.markdown("## 📋 New Patient Assessment")
    st.markdown("Enter patient clinical data below to analyze for possible irAEs.")
    
    # Initialize session state
    if "assessment_result" not in st.session_state:
        st.session_state.assessment_result = None
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["📝 Free Text Input", "📊 Structured Input"])
    
    with tab1:
        render_freetext_input()
    
    with tab2:
        render_structured_input()


def render_freetext_input():
    """Render free text input form."""
    st.markdown("### Enter Clinical Data as Free Text")
    st.info("💡 Paste clinical notes, lab results, and medication lists directly.")
    
    with st.form("freetext_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id = st.text_input("Patient ID (optional)")
            age = st.number_input("Age", min_value=0, max_value=120, value=65)
            cancer_type = st.text_input("Cancer Type", placeholder="e.g., Non-small cell lung cancer")
        
        with col2:
            st.markdown("**Immunotherapy Status**")
            on_immunotherapy = st.checkbox("Patient is on immunotherapy", value=True)
        
        st.markdown("---")
        
        # Free text inputs
        col1, col2 = st.columns(2)
        
        with col1:
            medications_text = st.text_area(
                "📦 Medications",
                height=150,
                placeholder="Enter medication list...\nExample:\nPembrolizumab 200mg IV q3weeks\nOndansetron 8mg PRN\nDexamethasone 4mg daily",
            )
            
            labs_text = st.text_area(
                "🔬 Laboratory Results",
                height=150,
                placeholder="Enter lab values...\nExample:\nAST 145 U/L (H)\nALT 178 U/L (H)\nTSH 0.1 mIU/L (L)\nCreatinine 1.2 mg/dL",
            )
        
        with col2:
            symptoms_text = st.text_area(
                "🩺 Symptoms",
                height=150,
                placeholder="Enter patient symptoms...\nExample:\nFatigue - moderate\nDiarrhea - 4 episodes/day\nRash on trunk",
            )
            
            notes_text = st.text_area(
                "📝 Clinical Notes",
                height=150,
                placeholder="Enter clinical notes, assessments, or other relevant information...",
            )
        
        st.markdown("---")
        
        # Analysis options
        col1, col2 = st.columns(2)
        with col1:
            use_llm = st.checkbox(
                "🤖 Use AI-enhanced analysis",
                value=False,
                help="Use LLM for additional clinical reasoning (requires API key)"
            )
        
        submitted = st.form_submit_button("🔍 Analyze for irAEs", type="primary", use_container_width=True)
        
        if submitted:
            # Create PatientData object
            patient_data = PatientData(
                patient_id=patient_id if patient_id else None,
                age=age if age > 0 else None,
                cancer_type=cancer_type if cancer_type else None,
                raw_medications=medications_text if medications_text else None,
                raw_labs=labs_text if labs_text else None,
                raw_symptoms=symptoms_text if symptoms_text else None,
                raw_notes=notes_text if notes_text else None,
            )
            
            # Parse structured data from free text
            if medications_text:
                med_parser = MedicationParser()
                patient_data.medications = med_parser.parse_medication_list(medications_text)
            
            if labs_text:
                lab_parser = LabParser()
                patient_data.labs = lab_parser.parse(labs_text)
            
            if symptoms_text:
                symptom_parser = SymptomParser()
                patient_data.symptoms = symptom_parser.parse(symptoms_text)
            
            # Run assessment
            run_assessment(patient_data, use_llm)


def render_structured_input():
    """Render structured input form."""
    st.markdown("### Enter Clinical Data in Structured Format")
    st.info("💡 Use this form for precise, structured data entry.")
    
    with st.form("structured_form"):
        # Patient info
        st.markdown("#### Patient Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            patient_id = st.text_input("Patient ID")
        with col2:
            age = st.number_input("Age", min_value=0, max_value=120, value=65)
        with col3:
            cancer_type = st.text_input("Cancer Type")
        
        st.markdown("---")
        
        # Medications
        st.markdown("#### 📦 Medications")
        st.markdown("Add immunotherapy and other medications:")
        
        # Immunotherapy selection
        col1, col2 = st.columns(2)
        with col1:
            immunotherapy_agent = st.selectbox(
                "Immunotherapy Agent",
                [
                    "None",
                    "Pembrolizumab (Keytruda)",
                    "Nivolumab (Opdivo)",
                    "Atezolizumab (Tecentriq)",
                    "Durvalumab (Imfinzi)",
                    "Ipilimumab (Yervoy)",
                    "Combination: Nivolumab + Ipilimumab",
                    "Other",
                ],
            )
        with col2:
            if immunotherapy_agent == "Other":
                other_agent = st.text_input("Specify immunotherapy agent")
        
        other_meds = st.text_area(
            "Other Medications (one per line)",
            height=100,
            placeholder="Dexamethasone 4mg daily\nOndansetron 8mg PRN",
        )
        
        st.markdown("---")
        
        # Labs
        st.markdown("#### 🔬 Laboratory Results")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ast = st.number_input("AST (U/L)", min_value=0.0, value=0.0)
            alt = st.number_input("ALT (U/L)", min_value=0.0, value=0.0)
        with col2:
            bilirubin = st.number_input("Bilirubin (mg/dL)", min_value=0.0, value=0.0)
            creatinine = st.number_input("Creatinine (mg/dL)", min_value=0.0, value=0.0)
        with col3:
            tsh = st.number_input("TSH (mIU/L)", min_value=0.0, value=0.0)
            glucose = st.number_input("Glucose (mg/dL)", min_value=0.0, value=0.0)
        with col4:
            troponin = st.number_input("Troponin (ng/mL)", min_value=0.0, value=0.0, format="%.3f")
            bnp = st.number_input("BNP (pg/mL)", min_value=0.0, value=0.0)
        
        st.markdown("---")
        
        # Vitals
        st.markdown("#### 📈 Vital Signs")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            temp = st.number_input("Temperature (°C)", min_value=35.0, max_value=42.0, value=37.0)
        with col2:
            hr = st.number_input("Heart Rate (bpm)", min_value=30, max_value=200, value=80)
        with col3:
            sbp = st.number_input("Systolic BP (mmHg)", min_value=60, max_value=250, value=120)
            dbp = st.number_input("Diastolic BP (mmHg)", min_value=30, max_value=150, value=80)
        with col4:
            spo2 = st.number_input("SpO2 (%)", min_value=50.0, max_value=100.0, value=98.0)
        
        st.markdown("---")
        
        # Symptoms
        st.markdown("#### 🩺 Symptoms")
        symptoms = st.multiselect(
            "Select presenting symptoms",
            [
                "Fatigue",
                "Weakness",
                "Diarrhea",
                "Abdominal pain",
                "Nausea/Vomiting",
                "Cough",
                "Shortness of breath",
                "Rash",
                "Itching (pruritus)",
                "Headache",
                "Confusion",
                "Chest pain",
                "Palpitations",
                "Joint pain",
                "Muscle weakness",
                "Numbness/Tingling",
                "Vision changes",
            ],
        )
        
        other_symptoms = st.text_input("Other symptoms (comma-separated)")
        
        st.markdown("---")
        
        # Clinical notes
        st.markdown("#### 📝 Clinical Notes")
        notes_text = st.text_area(
            "Additional clinical notes or context",
            height=100,
        )
        
        st.markdown("---")
        
        # Analysis options
        use_llm = st.checkbox(
            "🤖 Use AI-enhanced analysis",
            value=False,
            help="Use LLM for additional clinical reasoning (requires API key)"
        )
        
        submitted = st.form_submit_button("🔍 Analyze for irAEs", type="primary", use_container_width=True)
        
        if submitted:
            # Build patient data from structured inputs
            patient_data = build_patient_data_from_structured(
                patient_id, age, cancer_type,
                immunotherapy_agent, other_meds,
                ast, alt, bilirubin, creatinine, tsh, glucose, troponin, bnp,
                temp, hr, sbp, dbp, spo2,
                symptoms, other_symptoms,
                notes_text,
            )
            
            run_assessment(patient_data, use_llm)


def build_patient_data_from_structured(
    patient_id, age, cancer_type,
    immunotherapy_agent, other_meds,
    ast, alt, bilirubin, creatinine, tsh, glucose, troponin, bnp,
    temp, hr, sbp, dbp, spo2,
    symptoms, other_symptoms,
    notes_text,
) -> PatientData:
    """Build PatientData from structured form inputs."""
    now = datetime.now()
    
    # Build medications
    medications = []
    if immunotherapy_agent and immunotherapy_agent != "None":
        agent_name = immunotherapy_agent.split(" (")[0] if "(" in immunotherapy_agent else immunotherapy_agent
        medications.append(Medication(
            name=agent_name,
            is_immunotherapy=True,
            start_date=now,
        ))
    
    if other_meds:
        med_parser = MedicationParser()
        other_medications = med_parser.parse_medication_list(other_meds)
        medications.extend(other_medications)
    
    # Build labs
    labs = []
    if ast > 0:
        labs.append(LabResult(name="AST", value=ast, unit="U/L", 
                              reference_low=10, reference_high=40, date=now))
    if alt > 0:
        labs.append(LabResult(name="ALT", value=alt, unit="U/L",
                              reference_low=7, reference_high=56, date=now))
    if bilirubin > 0:
        labs.append(LabResult(name="Bilirubin", value=bilirubin, unit="mg/dL",
                              reference_low=0.1, reference_high=1.2, date=now))
    if creatinine > 0:
        labs.append(LabResult(name="Creatinine", value=creatinine, unit="mg/dL",
                              reference_low=0.7, reference_high=1.3, date=now))
    if tsh > 0:
        labs.append(LabResult(name="TSH", value=tsh, unit="mIU/L",
                              reference_low=0.4, reference_high=4.0, date=now))
    if glucose > 0:
        labs.append(LabResult(name="Glucose", value=glucose, unit="mg/dL",
                              reference_low=70, reference_high=100, date=now))
    if troponin > 0:
        labs.append(LabResult(name="Troponin", value=troponin, unit="ng/mL",
                              reference_low=0, reference_high=0.04, date=now))
    if bnp > 0:
        labs.append(LabResult(name="BNP", value=bnp, unit="pg/mL",
                              reference_low=0, reference_high=100, date=now))
    
    # Check for abnormal values
    for lab in labs:
        lab.is_abnormal = lab.check_abnormal()
    
    # Build vitals
    vitals = [VitalSigns(
        date=now,
        temperature=temp,
        heart_rate=hr,
        blood_pressure_systolic=sbp,
        blood_pressure_diastolic=dbp,
        oxygen_saturation=spo2,
    )]
    
    # Build symptoms
    symptom_list = []
    for symptom in symptoms:
        symptom_list.append(PatientSymptom(
            symptom=symptom,
            reported_date=now,
        ))
    
    if other_symptoms:
        for symptom in other_symptoms.split(","):
            symptom = symptom.strip()
            if symptom:
                symptom_list.append(PatientSymptom(
                    symptom=symptom,
                    reported_date=now,
                ))
    
    return PatientData(
        patient_id=patient_id if patient_id else None,
        age=age if age > 0 else None,
        cancer_type=cancer_type if cancer_type else None,
        medications=medications,
        labs=labs,
        vitals=vitals,
        symptoms=symptom_list,
        raw_notes=notes_text if notes_text else None,
    )


def run_assessment(patient_data: PatientData, use_llm: bool = False):
    """Run the irAE assessment and display results."""
    with st.spinner("🔍 Analyzing patient data for irAE signals..."):
        try:
            # Initialize assessment engine (without LLM for now)
            engine = IRAEAssessmentEngine(use_llm=False)
            
            # Run assessment
            result = engine.assess_sync(patient_data)
            
            # Store result in session state
            st.session_state.assessment_result = result
            st.session_state.patient_data = patient_data
            
            st.success("✅ Assessment complete!")
            
            # Display quick summary
            display_quick_summary(result)
            
            st.markdown("---")
            st.info("📊 Go to **Results** page for detailed findings and recommendations.")
            
        except Exception as e:
            st.error(f"❌ Error during assessment: {str(e)}")
            raise e


def display_quick_summary(result):
    """Display a quick summary of the assessment."""
    st.markdown("### 📊 Assessment Summary")
    
    # Urgency banner
    urgency_styles = {
        "🔴 Emergency evaluation": "urgency-emergency",
        "🟠 Urgent (same day)": "urgency-urgent",
        "🟡 Needs oncology review soon": "urgency-soon",
        "🟢 Routine monitoring": "urgency-routine",
    }
    
    urgency_class = urgency_styles.get(result.urgency.value, "urgency-routine")
    
    st.markdown(f"""
    <div class="{urgency_class}">
    <strong>Urgency Level:</strong> {result.urgency.value}<br>
    <strong>irAE Detected:</strong> {"Yes" if result.irae_detected else "No"}<br>
    <strong>Likelihood:</strong> {result.causality.likelihood.value}<br>
    <strong>Overall Severity:</strong> {result.overall_severity.value}
    </div>
    """, unsafe_allow_html=True)
    
    # Affected systems
    if result.irae_detected:
        affected = [f.system.value for f in result.affected_systems if f.detected]
        if affected:
            st.markdown(f"**Affected Systems:** {', '.join(affected)}")
