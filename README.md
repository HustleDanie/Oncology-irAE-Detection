---
title: Oncology irAE Detection
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
suggested_hardware: t4-small
---

# 🏥 Oncology irAE Clinical Safety Assistant

An AI-powered clinical decision support system for detecting, classifying, and triaging **immune-related adverse events (irAEs)** in oncology immunotherapy patients.

> ⚠️ **IMPORTANT SAFETY DISCLAIMER**: This tool is designed to **support** clinical decision-making, not replace it. All findings require clinician confirmation. Do not use this system for definitive diagnoses or treatment decisions.

## 🎯 Overview

Immunotherapy drugs (checkpoint inhibitors like pembrolizumab, nivolumab, ipilimumab) can cause immune-related adverse events affecting multiple organ systems. This assistant helps clinicians:

- **Detect** potential irAEs from clinical notes, labs, vitals, and symptoms
- **Classify** by organ system (GI, liver, lung, endocrine, skin, neuro, cardiac)
- **Grade** severity using CTCAE criteria (Grade 1-4)
- **Triage** urgency (routine → emergency)
- **Cite** supporting evidence from patient data

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📋 **Multi-source Parsing** | Parse clinical notes, lab values, medications, vitals, symptoms |
| 🔬 **Organ-Specific Analysis** | Dedicated analyzers for 7 organ systems |
| 📊 **CTCAE Grading** | Standardized severity grading (Grade 1-4) |
| 🚨 **Urgency Triage** | 🟢 Routine, 🟡 Soon, 🟠 Urgent, 🔴 Emergency |
| 🤖 **LLM Integration** | Optional GPT-4/Claude for enhanced clinical reasoning |
| 🖥️ **Web Interface** | Streamlit-based UI for clinicians |

## 📁 Project Structure

```
Oncology/
├── src/
│   ├── models/           # Pydantic data models
│   │   ├── patient.py    # Patient, labs, medications, vitals
│   │   └── assessment.py # irAE assessment, findings, causality
│   ├── parsers/          # Clinical data parsers
│   │   ├── lab_parser.py
│   │   ├── medication_parser.py
│   │   ├── symptom_parser.py
│   │   └── note_parser.py
│   ├── analyzers/        # Organ-specific irAE detection
│   │   ├── base.py       # Base analyzer class
│   │   ├── gi_analyzer.py
│   │   ├── liver_analyzer.py
│   │   ├── lung_analyzer.py
│   │   ├── endocrine_analyzer.py
│   │   ├── skin_analyzer.py
│   │   ├── neuro_analyzer.py
│   │   ├── cardiac_analyzer.py
│   │   └── immunotherapy_detector.py
│   ├── llm/              # LLM integration
│   │   ├── client.py     # OpenAI/Anthropic client
│   │   ├── prompts.py    # Prompt templates
│   │   └── assessment_engine.py
│   └── utils/            # Utilities
│       ├── constants.py  # Reference values, drug lists
│       └── formatting.py # Output formatting helpers
├── app/                  # Streamlit web application
│   ├── main.py          # Application entry point
│   └── pages/           # UI pages
│       ├── home.py
│       ├── assessment.py
│       ├── results.py
│       └── about.py
├── tests/               # Unit tests
│   ├── test_parsers.py
│   ├── test_analyzers.py
│   └── test_assessment.py
├── config/
│   └── settings.py      # Application settings
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project metadata
└── .env.example         # Environment variables template
```

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Oncology
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   copy .env.example .env   # Windows
   cp .env.example .env     # macOS/Linux
   
   # Edit .env with your API keys (optional)
   OPENAI_API_KEY=sk-your-key-here
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

## 💻 Usage

### Web Interface (Recommended)

Start the Streamlit application:

```bash
streamlit run app/main.py
```

Then open your browser to `http://localhost:8501`

### Programmatic Usage

```python
from src.models.patient import PatientData, LabResult, Medication
from src.llm.assessment_engine import IRAEAssessmentEngine
from config.settings import Settings

# Initialize the assessment engine
settings = Settings()
engine = IRAEAssessmentEngine(settings)

# Create patient data
patient = PatientData(
    patient_id="P001",
    age=65,
    sex="male",
    labs=[
        LabResult(name="ALT", value=250, unit="U/L", date="2024-01-15"),
        LabResult(name="AST", value=200, unit="U/L", date="2024-01-15"),
    ],
    medications=[
        Medication(name="pembrolizumab", dose="200mg", frequency="q3w", 
                   start_date="2023-10-01", category="immunotherapy")
    ]
)

# Run assessment
assessment = await engine.assess_patient(patient)

# View results
print(f"irAE Detected: {assessment.irae_detected}")
for finding in assessment.organ_findings:
    print(f"  {finding.organ_system}: {finding.condition} - Grade {finding.severity_grade}")
print(f"Urgency: {assessment.urgency_level}")
```

## 🔬 Supported Organ Systems

| System | Common irAEs | Key Markers |
|--------|-------------|-------------|
| **Hepatic** | Hepatitis, cholangitis | ALT, AST, bilirubin, ALP |
| **Gastrointestinal** | Colitis, enteritis | Diarrhea frequency, bloody stool, CRP |
| **Pulmonary** | Pneumonitis, ILD | Dyspnea, O2 sat, imaging findings |
| **Endocrine** | Thyroiditis, hypophysitis, adrenal insufficiency | TSH, T4, cortisol, glucose |
| **Dermatologic** | Rash, SJS/TEN, vitiligo | BSA involvement, mucosal lesions |
| **Neurologic** | Neuropathy, encephalitis, myasthenia | Weakness pattern, mental status |
| **Cardiac** | Myocarditis, arrhythmia, pericarditis | Troponin, BNP, ECG changes |

## 📊 CTCAE Severity Grading

| Grade | Severity | General Description |
|-------|----------|---------------------|
| **1** | Mild | Asymptomatic or mild symptoms; observation only |
| **2** | Moderate | Minimal intervention indicated; limiting ADL |
| **3** | Severe | Hospitalization indicated; disabling |
| **4** | Life-threatening | Urgent intervention indicated |

## 🚨 Urgency Levels

| Level | Icon | Action Timeframe |
|-------|------|------------------|
| **Routine** | 🟢 | Days to weeks |
| **Soon** | 🟡 | 24-48 hours |
| **Urgent** | 🟠 | Same day |
| **Emergency** | 🔴 | Immediate |

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_parsers.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT models | No* |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | No* |
| `LLM_PROVIDER` | `openai` or `anthropic` | No |
| `LLM_MODEL` | Model name (e.g., `gpt-4o`) | No |
| `DEBUG` | Enable debug mode | No |

*At least one API key required for LLM-enhanced analysis

### Settings File

Edit `config/settings.py` to customize:

- Default LLM provider and model
- Temperature and token limits
- Reference lab ranges
- Severity thresholds

## ⚠️ Safety Guidelines

### This System IS For:
- ✅ Clinical decision **support**
- ✅ Rapid screening and pattern detection
- ✅ Educational reference for irAE patterns
- ✅ Documentation assistance

### This System IS NOT For:
- ❌ Definitive diagnosis
- ❌ Autonomous treatment decisions
- ❌ Replacing clinical judgment
- ❌ Prescribing medications

### Best Practices
1. **Always verify** findings with clinical examination
2. **Consider alternative causes** (infection, disease progression)
3. **Document clinical reasoning** beyond AI suggestions
4. **Escalate appropriately** based on clinical gestalt
5. **Report discrepancies** to improve the system

## 📚 References

- [ASCO irAE Management Guidelines](https://www.asco.org/)
- [NCCN Guidelines: Immunotherapy-Related Toxicities](https://www.nccn.org/)
- [CTCAE v5.0](https://ctep.cancer.gov/protocoldevelopment/electronic_applications/ctc.htm)
- [SITC Toxicity Management Guidelines](https://www.sitcancer.org/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For questions, issues, or feedback, please open a GitHub issue or contact the development team.

---

**Remember**: This tool supports clinical decision-making. All findings require clinician verification before any clinical action is taken.
