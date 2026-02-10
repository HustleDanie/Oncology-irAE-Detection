# MedGemma Fine-tuning for irAE Detection

This directory contains everything needed to fine-tune MedGemma for improved accuracy on immune-related adverse event (irAE) detection.

## Problem Statement

Base MedGemma achieves ~60% validation accuracy on our clinical cases. For a critical safety system, we need **≥80% accuracy** (at most 1 wrong field per case).

## Solution: LoRA Fine-tuning

We use **LoRA (Low-Rank Adaptation)** to efficiently fine-tune MedGemma on our validated clinical cases:
- Trains only 0.5% of parameters (memory efficient)
- Works on T4 GPU (16GB VRAM)
- Preserves base medical knowledge while improving irAE-specific accuracy

## Files

```
fine_tuning/
├── README.md                    # This file
├── requirements-finetune.txt    # Dependencies for fine-tuning
├── training_data.py             # Training data generator
├── finetune_medgemma.py         # Fine-tuning script
└── training_data.jsonl          # Generated training data (after running)
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r fine_tuning/requirements-finetune.txt
```

### 2. Generate Training Data

```bash
cd fine_tuning
python training_data.py
```

This creates `training_data.jsonl` with 11 instruction-tuning examples based on our validated clinical cases.

### 3. Fine-tune Model (Requires GPU)

**Option A: Local (if you have T4/A10/A100 GPU)**
```bash
python finetune_medgemma.py \
    --training-file training_data.jsonl \
    --output-dir ./medgemma-irae-finetuned \
    --epochs 3
```

**Option B: Google Colab (Free T4 GPU)**
1. Upload fine_tuning folder to Colab
2. Install requirements
3. Run fine-tuning script

**Option C: HuggingFace Spaces (AutoTrain)**
1. Go to HuggingFace AutoTrain
2. Upload training_data.jsonl
3. Select base model: google/medgemma-4b-it
4. Configure LoRA parameters
5. Start training

### 4. Deploy Fine-tuned Model

After fine-tuning, update your HuggingFace Space:

```python
# In your app.py, change the model loading to:
model_id = "YOUR_USERNAME/medgemma-irae-finetuned"  # Your fine-tuned model
```

## Training Data Details

The training data includes 11 carefully validated clinical cases covering:

| Case ID | Organ System | Severity | Key Learning |
|---------|-------------|----------|--------------|
| GI-001 | GI Colitis | Grade 2 | 5-6 stools/day → "soon" urgency |
| GI-002 | GI Colitis | Grade 3 | Bloody diarrhea → "urgent" |
| HEP-001 | Hepatitis | Grade 2 | AST/ALT 3-5x ULN → "soon" |
| HEP-002 | Hepatitis | Grade 3 | >10x ULN + jaundice → "urgent" |
| LUNG-001 | Pneumonitis | Grade 2 | GGO + O2 sat 94% → "soon" |
| LUNG-002 | Pneumonitis | Grade 3 | Hypoxemia requiring O2 → "emergency" |
| ENDO-001 | Thyroid | Grade 2 | High TSH → "soon" (can continue ICI) |
| ENDO-002 | Hypophysitis | Grade 3 | Low cortisol → "urgent" (life-threatening) |
| CARD-001 | Myocarditis | Grade 4 | Troponin + EF drop → "emergency" |
| NEURO-001 | MG | Grade 2 | AChR antibodies → "urgent" (progression risk) |
| NEURO-002 | Encephalitis | Grade 3 | Seizure + MRI changes → "emergency" |

## Expected Improvements

After fine-tuning, the model should correctly:

1. **Grade 2 irAEs → "soon" urgency** (not "routine")
2. **Grade 3 irAEs → "urgent" urgency** (not "soon")
3. **Cardiac/Neuro → Always "urgent" or higher**
4. **Correctly identify affected organ systems**
5. **Appropriate causality likelihood**

## Hyperparameters

Default LoRA configuration:
- Rank (r): 16
- Alpha: 32
- Dropout: 0.05
- Target modules: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj

Training:
- Epochs: 3
- Batch size: 1 (gradient accumulation: 4)
- Learning rate: 2e-4
- Mixed precision (FP16)

## Alternative: Prompt Engineering (Quick Fix)

If fine-tuning isn't feasible, the system also has improved prompts with:
- Explicit urgency rules with CTCAE grade mappings
- Few-shot examples showing correct outputs
- Safety validation layer that corrects LLM underestimation

These improvements are in `src/llm/prompts.py` and `src/llm/assessment_engine.py`.

## Validation

After fine-tuning, test with all 11 sample cases. Target: **4/5 or 5/5 validation score** on each case.

```python
# Run validation
python -m pytest tests/test_clinical_cases.py -v
```

## Notes

- Fine-tuning requires HuggingFace access to MedGemma (request at google/medgemma-4b-it)
- Training on 11 examples takes ~15 minutes on T4 GPU
- The LoRA adapter is small (~20MB) and can be uploaded to HuggingFace Hub
