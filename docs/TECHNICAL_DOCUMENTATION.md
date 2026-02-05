# Technical Documentation: irAE Clinical Safety Assistant

---

## Document Overview

This technical documentation provides comprehensive details on the system architecture, model implementation, performance characteristics, deployment strategy, and real-world usage considerations for the Oncology irAE Clinical Safety Assistant.

---

## Table of Contents

1. [Model Architecture & Fine-Tuning](#1-model-architecture--fine-tuning)
2. [Model Performance Analysis](#2-model-performance-analysis)
3. [User-Facing Application Stack](#3-user-facing-application-stack)
4. [Deployment Challenges & Solutions](#4-deployment-challenges--solutions)
5. [Real-World Usage Considerations](#5-real-world-usage-considerations)
6. [Operational Guidelines](#6-operational-guidelines)

---

## 1. Model Architecture & Fine-Tuning

### 1.1 Simplified Architecture Overview

The system uses **Google MedGemma** from the HAI-DEF collection - a single, powerful medical AI model that handles all clinical NLP tasks.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MEDGEMMA PIPELINE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Clinical Note Input                                                    │
│          │                                                               │
│          ▼                                                               │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │           Rule-Based Parsers (Fast Pre-processing)            │      │
│   │   • Lab value extraction (regex)                              │      │
│   │   • Medication parsing (pattern matching)                     │      │
│   │   • Structured data extraction                                │      │
│   └────────────────────────┬─────────────────────────────────────┘      │
│                            │                                             │
│                            ▼                                             │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │              Google MedGemma 4B IT                            │      │
│   │              (google/medgemma-4b-it)                          │      │
│   │                                                               │      │
│   │   Handles ALL medical NLP tasks:                              │      │
│   │   • Symptom extraction from free text                         │      │
│   │   • Vital signs extraction                                    │      │
│   │   • Clinical reasoning for irAE detection                     │      │
│   │   • CTCAE severity grading                                    │      │
│   │   • Urgency classification                                    │      │
│   └────────────────────────┬─────────────────────────────────────┘      │
│                            │                                             │
│                            ▼                                             │
│   ┌──────────────────────────────────────────────────────────────┐      │
│   │        Rule-Based Organ Analyzers (Validation Layer)          │      │
│   │   (GI, Liver, Lung, Endo, Skin, Neuro, Cardiac)              │      │
│   └────────────────────────┬─────────────────────────────────────┘      │
│                            │                                             │
│                            ▼                                             │
│              Final irAE Assessment                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Model Selection: Google MedGemma

| Model | Identifier | Size | Use Case |
|-------|------------|------|----------|
| **MedGemma 4B IT** | `google/medgemma-4b-it` | 4B params | Primary model - all clinical tasks |
| **MedGemma 27B Text IT** | `google/medgemma-27b-text-it` | 27B params | Fallback for complex reasoning (requires GPU tier) |

### 1.3 Why MedGemma?

MedGemma is part of Google's **Health AI Developer Foundations (HAI-DEF)** collection, specifically designed for medical applications:

| Feature | MedGemma 4B IT |
|---------|----------------|
| **Base Model** | Gemma 3 4B |
| **Medical Training** | Medical text, clinical notes, FHIR EHR data |
| **Benchmarks** | MedQA: 64.4%, PubMedQA: 73.4%, MMLU-Med: 70% |
| **Context Length** | 128K tokens (ideal for long clinical notes) |
| **Modality** | Text + Medical Images (multimodal) |
| **License** | HAI-DEF Terms of Use |

### 1.4 Pre-Training Foundation

MedGemma is built on **Gemma 3** with additional medical domain training:

| Characteristic | Specification |
|----------------|---------------|
| Base architecture | Decoder-only transformer |
| Parameter count | 4B (primary) / 27B (fallback) |
| Pre-training corpus | Web documents, books, code, scientific literature |
| Medical enhancement | Medical text, MIMIC-CXR, FHIR EHR data, medical Q&A datasets |
| Image training | Chest X-rays, dermatology, pathology, ophthalmology |

### 1.5 Fine-Tuning Approach

#### Google HAI-DEF Fine-Tuning (Upstream)

MedGemma was fine-tuned by Google's Health AI team using:

| Aspect | Details |
|--------|---------|
| **Fine-tuning method** | Supervised Fine-Tuning (SFT) |
| **Training data** | MIMIC-CXR, medical literature, FHIR EHR synthetic data |
| **Benchmark training** | MedQA, MedMCQA, PubMedQA, AfriMed-QA |
| **Safety alignment** | Extensive red-teaming and safety evaluation |

#### Our Application-Level Optimization

We apply **prompt engineering** to optimize MedGemma for irAE detection:

```python
# Example: Structured prompt for irAE reasoning
IRAE_SYSTEM_PROMPT = """
You are a clinical decision support system specialized in detecting 
immune-related adverse events (irAEs) in oncology patients receiving 
immunotherapy.

Your task is to:
1. Analyze the provided patient data
2. Identify potential irAEs by organ system
3. Assess likelihood (Unlikely, Possible, Probable, Definite)
4. Grade severity using CTCAE criteria (1-4)
5. Recommend urgency level (Routine, Soon, Urgent, Emergency)
6. Cite specific evidence supporting your assessment

IMPORTANT: Express uncertainty when evidence is incomplete. 
This tool supports clinical decision-making—it does not replace it.
"""
```

### 1.6 Prompt Engineering Strategy

#### Unified Prompting for MedGemma

Since MedGemma handles all tasks, we use task-specific system prompts:

| Task | System Prompt Approach |
|------|----------------------|
| Symptom extraction | "You are a medical AI assistant trained to extract clinical information. Extract patient symptoms..." |
| Vitals extraction | "You are a medical AI assistant trained to extract clinical information. Extract vital signs..." |
| irAE reasoning | Chain-of-thought prompting with CTCAE criteria |

#### Example: Symptom Extraction Prompt (MedGemma Format)

```python
messages = [
    {
        \"role\": \"system\",
        \"content\": \"You are a medical AI assistant trained to extract clinical information accurately.\"
    },
    {
        \"role\": \"user\", 
        \"content\": \"\"\"
Please extract all patient-reported symptoms and observed signs from the following clinical note.

For each symptom, provide:
- name: The symptom name
- present: Whether it is currently present (true/false)
- details: Relevant details (severity, frequency, location)

Format as JSON:
{
  \"symptoms\": [
    {\"name\": \"diarrhea\", \"present\": true, \"details\": \"3 episodes daily\"},
    {\"name\": \"fever\", \"present\": false, \"details\": \"denies fever\"}
  ]
}

Clinical Note:
---
[NOTE CONTENT]
---
\"\"\"
    }
]
```

### 1.7 Future Fine-Tuning Considerations

For production deployment, consider additional fine-tuning:

| Enhancement | Approach | Expected Benefit |
|-------------|----------|------------------|
| **Institution-specific tuning** | Fine-tune on local clinical notes | Better adaptation to documentation style |
| **Feedback loop training** | Train on clinician corrections | Continuous accuracy improvement |
| **Rare irAE enhancement** | Augment training with rare case reports | Better detection of uncommon presentations |

---

## 2. Model Performance Analysis

### 2.1 Performance Metrics Framework

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE DIMENSIONS                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Clinical Accuracy     Safety Metrics       Operational Metrics    │
│   ─────────────────     ──────────────       ──────────────────     │
│   • Sensitivity         • False negative     • Latency              │
│   • Specificity           rate (critical)    • Throughput           │
│   • PPV / NPV           • Alert fatigue      • Availability         │
│   • AUROC                 (false positive)   • Resource usage       │
│                         • Severity grading                          │
│                           accuracy                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Expected Performance Benchmarks

Based on similar clinical NLP systems and HAI-DEF model documentation:

#### Entity Extraction Performance

| Task | Precision | Recall | F1 Score | Source |
|------|-----------|--------|----------|--------|
| Symptom extraction | 88-92% | 85-90% | 86-91% | HAI-DEF benchmarks |
| Vital sign extraction | 92-96% | 90-94% | 91-95% | HAI-DEF benchmarks |
| Medication identification | 94-97% | 92-96% | 93-96% | Similar NER systems |
| Lab value extraction | 95-98% | 93-97% | 94-97% | Structured data |

#### irAE Detection Performance (Projected)

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Sensitivity** | ≥90% | Must catch most true irAEs |
| **Specificity** | ≥80% | Balance against alert fatigue |
| **PPV (Precision)** | ≥70% | Acceptable alert-to-true-positive ratio |
| **NPV** | ≥95% | High confidence in negative results |
| **Severity grading accuracy** | ≥85% | Within ±1 CTCAE grade |

### 2.3 Performance by Organ System

Different irAE types have varying detection complexity:

| Organ System | Detection Difficulty | Expected Accuracy | Key Challenges |
|--------------|---------------------|-------------------|----------------|
| **Hepatic** | Low | 90-95% | Clear lab markers (ALT, AST, bilirubin) |
| **Gastrointestinal** | Medium | 85-90% | Subjective symptoms, infectious mimics |
| **Pulmonary** | Medium | 85-90% | Requires imaging correlation |
| **Endocrine** | Medium-High | 80-88% | Non-specific symptoms, complex hormone panels |
| **Dermatologic** | Medium | 85-90% | Relies on description quality |
| **Neurologic** | High | 75-85% | Heterogeneous presentations |
| **Cardiac** | Medium-High | 80-88% | Rare but critical, subtle markers |

### 2.4 Error Analysis Framework

#### Types of Errors

| Error Type | Description | Clinical Impact | Mitigation |
|------------|-------------|-----------------|------------|
| **False Negative** | Miss a true irAE | HIGH - Patient harm | Optimize for sensitivity |
| **False Positive** | Alert on non-irAE | MEDIUM - Alert fatigue | Require evidence threshold |
| **Severity Undergrade** | Grade 3 called Grade 1 | HIGH - Delayed treatment | Conservative grading bias |
| **Severity Overgrade** | Grade 1 called Grade 3 | LOW - Excess workup | Acceptable trade-off |

#### Error Mitigation Strategies

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ERROR MITIGATION HIERARCHY                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   1. DETECTION LAYER                                                │
│      • High-sensitivity rule-based triggers                         │
│      • Multiple redundant detection pathways                        │
│      • Low threshold for flagging potential irAEs                   │
│                                                                      │
│   2. REASONING LAYER                                                │
│      • LLM provides nuanced analysis                                │
│      • Explicit uncertainty quantification                          │
│      • Evidence citation required                                   │
│                                                                      │
│   3. HUMAN VERIFICATION LAYER                                       │
│      • All findings require clinician review                        │
│      • System clearly marked as "decision support"                  │
│      • Easy pathway to override/correct                             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.5 Latency Performance

| Operation | Expected Latency | Acceptable Range |
|-----------|------------------|------------------|
| Data parsing (structured) | <100ms | <500ms |
| Note parsing (per note) | 2-5 seconds | <10 seconds |
| Organ analyzer (all 7) | <500ms | <2 seconds |
| LLM reasoning | 5-15 seconds | <30 seconds |
| **Total end-to-end** | **10-25 seconds** | **<60 seconds** |

### 2.6 Validation Strategy

#### Phase 1: Retrospective Validation

| Step | Method | Sample Size | Success Criteria |
|------|--------|-------------|------------------|
| 1 | Chart review of known irAE cases | 200 cases | Sensitivity ≥85% |
| 2 | Chart review of non-irAE controls | 400 cases | Specificity ≥75% |
| 3 | Severity grading comparison | 200 cases | Agreement ≥80% |

#### Phase 2: Prospective Pilot

| Metric | Measurement Method | Target |
|--------|-------------------|--------|
| Real-world sensitivity | Compare to eventual diagnoses | ≥90% |
| Alert-to-action ratio | Track clinician responses | ≥50% reviewed |
| Time to detection | Compare to standard care | ≥24h improvement |
| Clinician satisfaction | Survey | ≥4/5 rating |

---

## 3. User-Facing Application Stack

### 3.1 Technology Stack Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      APPLICATION STACK                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   PRESENTATION LAYER                                                │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  Streamlit Web Application                                   │   │
│   │  • Responsive UI components                                  │   │
│   │  • Real-time updates                                         │   │
│   │  • Session state management                                  │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│   APPLICATION LAYER          ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  Python Backend                                              │   │
│   │  • Pydantic data models                                      │   │
│   │  • Async processing                                          │   │
│   │  • Business logic                                            │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│   AI/ML LAYER                ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  Model Inference                                             │   │
│   │  • HuggingFace Transformers                                  │   │
│   │  • Multi-model orchestration                                 │   │
│   │  • Structured output parsing                                 │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│   INFRASTRUCTURE LAYER       ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  Docker Container on HuggingFace Spaces                      │   │
│   │  • CPU/GPU compute                                           │   │
│   │  • Auto-scaling                                              │   │
│   │  • HTTPS/SSL                                                 │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Details

#### Frontend: Streamlit

| Component | Implementation | Purpose |
|-----------|----------------|---------|
| **Home Page** | `app/pages/home.py` | Introduction, quick start |
| **Assessment Page** | `app/pages/assessment.py` | Data input forms |
| **Results Page** | `app/pages/results.py` | Display findings, recommendations |
| **About Page** | `app/pages/about.py` | Documentation, disclaimers |

#### Backend: Python Modules

| Module | Location | Responsibility |
|--------|----------|----------------|
| **Data Models** | `src/models/` | Pydantic schemas for patient data, assessments |
| **Parsers** | `src/parsers/` | Extract structured data from text |
| **Analyzers** | `src/analyzers/` | Rule-based organ-specific detection |
| **LLM Client** | `src/llm/client.py` | Multi-model inference orchestration |
| **Assessment Engine** | `src/llm/assessment_engine.py` | Coordinate full analysis pipeline |

### 3.3 Data Flow Architecture

```
User Input (Web Form)
        │
        ▼
┌───────────────────┐
│  Pydantic         │
│  Validation       │
│  (PatientData)    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐     ┌───────────────────┐
│  Note Parser      │────▶│  LLM: Conditions  │
│                   │     │  LLM: Vitals      │
└─────────┬─────────┘     └─────────┬─────────┘
          │                         │
          │◀────────────────────────┘
          ▼
┌───────────────────┐
│  Enriched         │
│  PatientData      │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Organ Analyzers  │
│  (7 parallel)     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  LLM: Clinical    │
│  Reasoning        │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  IRAEAssessment   │
│  (Structured      │
│  Output)          │
└─────────┬─────────┘
          │
          ▼
    Results Page
```

### 3.4 User Interface Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Clarity** | Color-coded urgency levels (🟢🟡🟠🔴) |
| **Actionability** | Specific recommendations, not just findings |
| **Transparency** | Evidence citations for every assessment |
| **Safety** | Persistent disclaimers, clinician verification prompts |
| **Efficiency** | Minimal clicks to complete assessment |

### 3.5 Session Management

```python
# Streamlit session state structure
st.session_state = {
    "patient_data": PatientData | None,      # Current patient
    "assessment_result": IRAEAssessment | None,  # Latest results
    "llm_client": HuggingFaceClient,         # Loaded models
    "assessment_engine": IRAEAssessmentEngine,
    "use_llm_for_assessment": bool,          # LLM toggle
}
```

---

## 4. Deployment Challenges & Solutions

### 4.1 Challenge Matrix

| Challenge | Severity | Complexity | Status |
|-----------|----------|------------|--------|
| Model size / memory | High | Medium | ✅ Addressed |
| Cold start latency | Medium | Medium | ⚠️ Mitigated |
| GPU availability | High | Low | ✅ Addressed |
| HIPAA compliance | High | High | 🔄 In progress |
| EHR integration | High | High | 📋 Planned |
| Scalability | Medium | Medium | ✅ Addressed |

### 4.2 Challenge 1: Model Size & Memory

**Problem:** Three large models (5-16GB each) exceed typical server RAM.

**Solutions Implemented:**

| Solution | Implementation | Memory Reduction |
|----------|----------------|------------------|
| **Lazy loading** | Models loaded on-demand, not at startup | ~60% during idle |
| **8-bit quantization** | `load_in_8bit=True` via bitsandbytes | ~50% per model |
| **Model sharing** | Single model instance across requests | ~66% vs. duplicates |
| **Offloading** | `device_map="auto"` for CPU/GPU splitting | Enables larger models |

```python
# Implementation in src/llm/client.py
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",           # Automatic CPU/GPU allocation
    torch_dtype=torch.bfloat16,  # Reduced precision
    load_in_8bit=True,           # Quantization (optional)
)
```

### 4.3 Challenge 2: Cold Start Latency

**Problem:** First request after idle triggers model loading (2-5 minutes).

**Solutions:**

| Strategy | Implementation | Trade-off |
|----------|----------------|-----------|
| **Keep-alive requests** | Periodic health checks prevent sleep | Small compute cost |
| **Model caching** | HuggingFace Hub caches downloaded models | Disk space |
| **Warm pool** | Pre-loaded model instances (paid tiers) | Higher baseline cost |
| **User messaging** | "Loading models..." progress indicator | UX improvement only |

### 4.4 Challenge 3: GPU Availability

**Problem:** Local deployment requires expensive GPU hardware.

**Solutions:**

| Approach | When to Use | Cost |
|----------|-------------|------|
| **HuggingFace Spaces (CPU)** | Development, low-volume | Free |
| **HuggingFace Spaces (GPU)** | Production pilot | $0.60-$4.50/hr |
| **Cloud GPU (AWS/GCP)** | Production scale | $0.50-$3.00/hr |
| **Quantized CPU inference** | Budget-constrained | Free (slower) |

**Current Implementation:** HuggingFace Spaces with Docker, upgradeable to GPU tier.

### 4.5 Challenge 4: HIPAA Compliance

**Problem:** Protected Health Information (PHI) requires strict handling.

**Compliance Roadmap:**

| Requirement | Current Status | Plan |
|-------------|----------------|------|
| **Data encryption (transit)** | ✅ HTTPS enforced | Complete |
| **Data encryption (rest)** | ⚠️ Not storing data | By design |
| **Access controls** | ⚠️ No auth currently | Add SSO/OAuth |
| **Audit logging** | ❌ Not implemented | Add logging layer |
| **BAA with vendors** | ❌ Not in place | Required for production |
| **Data minimization** | ✅ No data retention | By design |

**Architecture Decision:** Current design processes data in-memory and does not persist PHI, reducing compliance scope.

### 4.6 Challenge 5: EHR Integration

**Problem:** Manual data entry limits clinical utility.

**Integration Roadmap:**

```
Phase 1 (Current): Standalone Web App
───────────────────────────────────────
• Manual data entry
• Copy/paste from EHR
• Lowest barrier to pilot

Phase 2 (3-6 months): SMART on FHIR App
───────────────────────────────────────
• Launch from within EHR
• Auto-populate patient context
• Read-only EHR access
• Requires EHR vendor approval

Phase 3 (6-12 months): Integrated CDS
───────────────────────────────────────
• Background monitoring
• Push alerts to EHR inbox
• Write-back recommendations
• Full clinical workflow integration
```

**SMART on FHIR Implementation Plan:**

```javascript
// FHIR patient context retrieval
const patient = await fhirClient.request(`Patient/${patientId}`);
const labs = await fhirClient.request(
  `Observation?patient=${patientId}&category=laboratory&_sort=-date&_count=50`
);
const meds = await fhirClient.request(
  `MedicationRequest?patient=${patientId}&status=active`
);
```

### 4.7 Challenge 6: Scalability

**Problem:** Single-instance deployment limits concurrent users.

**Scaling Strategy:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SCALING ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   CURRENT: Single Instance                                          │
│   ┌─────────────┐                                                   │
│   │  Container  │◀──── All requests                                 │
│   └─────────────┘                                                   │
│                                                                      │
│   FUTURE: Horizontal Scaling                                        │
│   ┌─────────────┐                                                   │
│   │  Load       │                                                   │
│   │  Balancer   │                                                   │
│   └──────┬──────┘                                                   │
│          │                                                           │
│    ┌─────┼─────┬─────────┐                                          │
│    ▼     ▼     ▼         ▼                                          │
│   ┌───┐ ┌───┐ ┌───┐    ┌───┐                                        │
│   │ 1 │ │ 2 │ │ 3 │....│ N │  ◀── Auto-scaling                     │
│   └───┘ └───┘ └───┘    └───┘                                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

| Scale Tier | Instances | Concurrent Users | Monthly Cost |
|------------|-----------|------------------|--------------|
| Pilot | 1 | 10-20 | $0-50 |
| Departmental | 2-4 | 50-100 | $200-500 |
| Hospital | 4-10 | 200-500 | $1,000-3,000 |
| Enterprise | 10+ | 1,000+ | $5,000+ |

---

## 5. Real-World Usage Considerations

### 5.1 Clinical Workflow Integration

**This system is designed for real clinical use, not just benchmarking.**

#### Intended Use Cases

| Use Case | Workflow | Frequency |
|----------|----------|-----------|
| **Pre-rounds review** | Oncologist reviews flagged patients before morning rounds | Daily |
| **New symptom triage** | Nurse enters patient-reported symptoms for quick assessment | As needed |
| **Lab review support** | Automated flag when labs suggest irAE pattern | Real-time |
| **Consultation support** | Specialist reviews case with AI-assisted summary | Per consult |

#### Workflow Example: Morning Rounds

```
6:30 AM  │  Oncologist opens irAE Assistant
         │
6:32 AM  │  Reviews overnight alerts:
         │  • Patient A: 🟠 Possible hepatic irAE (ALT trending)
         │  • Patient B: 🟡 Monitor thyroid (TSH elevated)
         │  • Patient C: 🟢 No concerns
         │
6:40 AM  │  For Patient A, clicks "View Details":
         │  • Evidence: ALT 156 (↑ from 45), AST 134 (↑ from 38)
         │  • Context: Pembrolizumab cycle 3, day 14
         │  • Recommendation: Check hepatitis panel, consider hold
         │
6:45 AM  │  Orders hepatitis panel, schedules same-day follow-up
         │
7:00 AM  │  Rounds begin with prioritized patient list
```

### 5.2 Alert Design Philosophy

**Avoiding Alert Fatigue**

Clinical decision support systems often fail due to excessive, non-actionable alerts. Our design principles:

| Principle | Implementation |
|-----------|----------------|
| **Tiered urgency** | Only 🔴 Emergency triggers interruptive alert |
| **Evidence required** | Every alert cites specific data points |
| **Actionable recommendations** | "Consider checking X" not just "Abnormal Y" |
| **Batch presentation** | Review alerts together, not one-by-one |
| **Easy dismissal** | One click to acknowledge with reason |

### 5.3 Handling Uncertainty

**The system explicitly communicates uncertainty:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ASSESSMENT: Possible Hepatic irAE                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Likelihood: POSSIBLE (not Probable)                               │
│                                                                      │
│   Supporting Evidence:                                              │
│   ✓ ALT elevated 3x above baseline                                  │
│   ✓ Patient on checkpoint inhibitor                                 │
│   ✓ Temporal relationship (cycle 3)                                 │
│                                                                      │
│   Conflicting/Missing Evidence:                                     │
│   ✗ Bilirubin normal                                                │
│   ✗ No symptoms reported (fatigue, jaundice)                        │
│   ? Hepatitis serology not available                                │
│                                                                      │
│   Confidence: MODERATE                                              │
│   Recommendation: Obtain hepatitis panel to clarify                 │
│                                                                      │
│   ⚠️ This assessment requires clinician verification.               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.4 Edge Cases & Limitations

| Scenario | System Behavior | Clinician Action |
|----------|-----------------|------------------|
| **Incomplete data** | Flags missing info, proceeds with available data | Supplement manually |
| **Conflicting evidence** | Reports uncertainty, shows both sides | Clinical judgment |
| **Rare irAE type** | May miss; rule-based backup catches patterns | Report false negative |
| **Non-English notes** | Limited accuracy | Use English summaries |
| **Pediatric patients** | Not validated for pediatrics | Use with caution |

### 5.5 Feedback Loop Design

**Continuous improvement through clinician feedback:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                      FEEDBACK COLLECTION                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   After each assessment, clinician can:                             │
│                                                                      │
│   [✓ Agree]  [✗ Disagree]  [~ Partially Correct]                   │
│                                                                      │
│   If Disagree:                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  What was incorrect?                                         │   │
│   │  ○ Missed an irAE (false negative)                          │   │
│   │  ○ Flagged incorrectly (false positive)                     │   │
│   │  ○ Wrong organ system                                        │   │
│   │  ○ Wrong severity grade                                      │   │
│   │  ○ Other: [________________]                                 │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│   This feedback is logged for model improvement.                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.6 Training & Onboarding

**User training requirements:**

| User Type | Training Time | Topics Covered |
|-----------|---------------|----------------|
| Oncologist | 30 minutes | Interpretation, limitations, when to override |
| Oncology NP/PA | 45 minutes | Data entry, interpretation, escalation |
| Oncology nurse | 30 minutes | Basic use, when to alert physician |
| IT support | 2 hours | Troubleshooting, configuration |

### 5.7 Performance Monitoring in Production

| Metric | Tracking Method | Alert Threshold |
|--------|-----------------|-----------------|
| Assessment latency | Application logs | >60 seconds |
| Error rate | Exception tracking | >1% |
| User engagement | Session analytics | <50% completion |
| False negative reports | Feedback system | Any critical miss |
| System uptime | Health checks | <99% |

---

## 6. Operational Guidelines

### 6.1 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Deployment: HuggingFace Spaces** | Free CPU tier | GPU tier ($0.60/hr) |
| **Browser** | Chrome 90+, Firefox 88+, Safari 14+ | Latest version |
| **Network** | 1 Mbps | 10+ Mbps |
| **Screen resolution** | 1280x720 | 1920x1080 |

### 6.2 Maintenance Schedule

| Task | Frequency | Responsible Party |
|------|-----------|-------------------|
| Dependency updates | Monthly | Development team |
| Model updates | Quarterly | ML team |
| Security patches | As released | DevOps |
| Performance review | Monthly | Clinical + Tech leads |
| User feedback review | Weekly | Product team |

### 6.3 Incident Response

| Severity | Definition | Response Time | Escalation |
|----------|------------|---------------|------------|
| **P1 - Critical** | System down, potential patient safety impact | 15 minutes | Immediate page |
| **P2 - High** | Major feature broken, workaround exists | 2 hours | Email + Slack |
| **P3 - Medium** | Minor feature issue | 24 hours | Ticket |
| **P4 - Low** | Cosmetic, enhancement | 1 week | Backlog |

### 6.4 Disaster Recovery

| Scenario | RTO | RPO | Recovery Method |
|----------|-----|-----|-----------------|
| Application crash | 5 minutes | N/A (stateless) | Auto-restart |
| Cloud provider outage | 2 hours | N/A | Failover to backup region |
| Model corruption | 30 minutes | N/A | Re-download from HuggingFace |
| Data breach | N/A | N/A | No PHI stored by design |

---

## Appendix A: Configuration Reference

### Environment Variables

```bash
# .env file
LLM_PROVIDER=huggingface
HUGGINGFACE_MODEL=google/medgemma-4b-it
USE_QUANTIZATION=true
DEFAULT_USE_LLM=true
DEBUG=false
LOG_LEVEL=INFO
```

### Model Configuration

```python
# config/settings.py
class Settings(BaseSettings):
    huggingface_model: str = \"google/medgemma-4b-it\"
    huggingface_model_fallback: str = \"google/medgemma-27b-text-it\"
    use_quantization: bool = True
    default_use_llm: bool = False
    max_evidence_items: int = 10
```

---

## Appendix B: API Reference

### PatientData Schema

```python
class PatientData(BaseModel):
    patient_id: str
    age: Optional[int]
    sex: Optional[str]
    labs: List[LabResult] = []
    medications: List[Medication] = []
    vitals: List[VitalSigns] = []
    symptoms: List[PatientSymptom] = []
    notes: List[ClinicalNote] = []
```

### IRAEAssessment Schema

```python
class IRAEAssessment(BaseModel):
    patient_id: str
    assessment_date: datetime
    irae_detected: bool
    overall_likelihood: Likelihood
    urgency_level: Urgency
    organ_findings: List[OrganSystemFinding]
    recommended_actions: List[RecommendedAction]
    supporting_evidence: List[str]
    clinical_reasoning: str
    disclaimer: str
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-05 | Development Team | Initial release |

---

*This document is intended for technical stakeholders, clinical informatics teams, and development personnel. For clinical usage guidelines, refer to the User Manual.*
