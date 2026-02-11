# 🎬 Hackathon Video Script: Oncology irAE Detection Assistant

**Total Duration: 3 minutes**

---

## ⏱️ 0:00 - 0:20 | THE HOOK (20 seconds)

### What to say:
> "Every year, **thousands of cancer patients die** not from their cancer, but from the **side effects of their treatment**. Immunotherapy saves lives, but it can also trigger dangerous immune attacks on the patient's own organs. Doctors call these **irAEs** - immune-related adverse events. The problem? They're **easy to miss** until it's too late."

### What to show:
- Quick stats on screen: "44% of immunotherapy patients experience irAEs"
- "Cardiac irAEs have 25-50% mortality rate"

---

## ⏱️ 0:20 - 0:50 | THE PROBLEM (30 seconds)

### What to say:
> "Here's the challenge: A busy oncologist sees **50+ patients a day**. irAE symptoms are buried in lab results, clinical notes, and vital signs. A Grade 2 colitis can escalate to Grade 4 **within 48 hours** if missed. Current EHR systems don't flag these patterns. By the time it's obvious, patients are in the ICU."

### Key stats to mention:
- Oncologists have ~15 minutes per patient
- irAE symptoms mimic common conditions (fatigue, diarrhea, cough)
- Early detection = better outcomes, but it requires connecting dots across multiple data sources

### What to show:
- Example of messy clinical data
- Timeline showing rapid escalation

---

## ⏱️ 0:50 - 1:40 | THE SOLUTION (50 seconds)

### What to say:
> "We built an **AI-powered clinical safety assistant** using Google's **MedGemma** - a medical language model trained on clinical data. It analyzes patient records in real-time and does three critical things:"

### The 3 Key Features (show each):

**1. DETECT** (10 sec)
> "It scans medications, labs, symptoms, and clinical notes to detect irAE patterns across **9 organ systems** - GI, liver, lung, endocrine, cardiac, neuro, skin, renal, and hematologic."

**2. GRADE** (10 sec)
> "It applies **CTCAE grading** - the gold standard for oncology toxicity - to classify severity from Grade 1 mild to Grade 4 life-threatening."

**3. TRIAGE** (10 sec)
> "Most importantly, it assigns **urgency levels**. Grade 3 hepatitis? Same-day evaluation. Cardiac involvement? Always emergency. It **cannot be overridden** - patient safety is hardcoded."

### Technical differentiator:
> "What makes this special? We use **MedGemma as the primary reasoning engine**, not just a chatbot wrapper. Rule-based validators ensure safety floors are never violated - even if the AI makes a mistake, the system catches it."

### What to show:
- Live demo: Paste clinical case → Get structured assessment
- Show the JSON output with severity, urgency, recommendations
- Highlight the safety corrections in action

---

## ⏱️ 1:40 - 2:20 | THE DEMO (40 seconds)

### What to say:
> "Let me show you. Here's a real case: 58-year-old on pembrolizumab with 5-6 loose stools daily for 4 days."

> "Watch what happens... The system detects **Grade 2 GI colitis**, assigns urgency **'soon'** - meaning oncology review in 1-3 days - and recommends holding immunotherapy and starting steroids."

> "Now here's the critical part - if I tried to mark this as 'routine monitoring', the **SafetyValidator blocks it**. Grade 2 can NEVER be routine. That's built into the code."

### What to show:
- Streamlit UI with sample case
- Real-time assessment generation
- Point to: severity, urgency, recommended actions
- Show safety correction message

---

## ⏱️ 2:20 - 2:45 | TECHNICAL CREDIBILITY (25 seconds)

### What to say:
> "Under the hood: **MedGemma 4B** with optimized prompts, **126 passing tests** covering all CTCAE grades, **9 organ-specific analyzers**, and an **accuracy monitoring system** that tracks every prediction for continuous improvement."

> "The architecture is **MedGemma-first** - the AI does the clinical reasoning, rule-based systems validate for safety. Best of both worlds."

### Key numbers to flash on screen:
| Metric | Value |
|--------|-------|
| Tests | 126 passing |
| Organ Systems | 9 |
| CTCAE Grades | 1-4 covered |
| Prompt Size | 80% smaller than GPT prompts |
| Safety Rules | Cannot be bypassed |

### What to show:
- Quick flash of test results
- Architecture diagram (MedGemma → Rule-based → SafetyValidator)

---

## ⏱️ 2:45 - 3:00 | THE CLOSE (15 seconds)

### What to say:
> "This isn't about replacing oncologists - it's about giving them **superpowers**. Catching the Grade 2 colitis before it becomes Grade 4. Flagging the subtle troponin rise that signals myocarditis."

> "Because in oncology, **every hour matters**. And no patient should die from a side effect we could have caught."

### Final screen:
- Project name: **Oncology irAE Clinical Safety Assistant**
- GitHub: `github.com/HustleDanie/Oncology-irAE-Detection`
- Built with: MedGemma, Python, Streamlit

---

## 🎯 KEY MESSAGES TO REMEMBER

1. **Problem is real and urgent** - People die from missed irAEs
2. **Solution is technical AND clinical** - Not just AI hype, actual CTCAE grading
3. **Safety is non-negotiable** - Hardcoded rules, cannot be overridden
4. **Demo speaks louder than slides** - Show the actual system working
5. **Human + AI collaboration** - Supports clinicians, doesn't replace them

---

## 📝 PRACTICE TIPS

- **Speak slower than you think** - 3 minutes goes fast
- **Practice the demo 5x** - Make sure it doesn't break live
- **Have backup screenshots** - In case of technical issues
- **End strong** - "Every hour matters" is your memorable close
- **Smile and be confident** - You built something that can save lives

---

## 🚫 DON'T SAY

- ❌ "It's just a wrapper around an LLM"
- ❌ "It diagnoses patients" (it SUPPORTS diagnosis)
- ❌ "It's 100% accurate" (no AI is)
- ❌ Technical jargon without explanation

## ✅ DO SAY

- ✅ "Clinical decision SUPPORT"
- ✅ "Safety-first architecture"
- ✅ "Built on published CTCAE guidelines"
- ✅ "Designed WITH clinician workflows in mind"

---

## 🎬 RECORDING CHECKLIST

- [ ] Streamlit app running and tested
- [ ] Sample cases ready (GI-001, CARD-001)
- [ ] Screen recording software ready
- [ ] Microphone tested
- [ ] Quiet environment
- [ ] Timer visible to track 3 minutes
- [ ] Backup demo video recorded (just in case)

---

**Good luck! You've built something genuinely impactful. Let that confidence show.** 🚀
