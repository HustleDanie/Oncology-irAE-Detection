<!-- Oncology Immunotherapy irAE Detection Assistant -->

# Project: Oncology irAE Clinical Safety Assistant

## Overview
AI-powered clinical decision support system for detecting, classifying, and triaging immune-related adverse events (irAEs) in oncology immunotherapy patients.

## Tech Stack
- Python 3.11+
- Streamlit (web interface)
- Google MedGemma (HAI-DEF) via Hugging Face (LLM backend)
- Pydantic (data validation)

## Key Features
- Parse clinical notes, labs, vitals, medications
- Detect organ-specific irAE patterns (GI, liver, lung, endocrine, skin, neuro, cardiac)
- CTCAE severity grading (Grade 1-4)
- Urgency triage classification
- Structured clinical output format

## Project Structure
```
/src
  /analyzers      - Organ-specific irAE detection modules
  /models         - Pydantic data models
  /parsers        - Clinical data parsers
  /utils          - Helper utilities
/app              - Streamlit web application
/tests            - Unit tests
/config           - Configuration files
```

## Safety Guidelines
- This tool supports clinical decision-making, not replacement
- Always emphasize clinician confirmation
- Express uncertainty when evidence is incomplete
- Do not prescribe drugs or provide definitive diagnoses
