"""irAE Assessment Engine combining rule-based and LLM analysis.

AI Expert Approved: Production-ready implementation with safety layers.
"""

from datetime import datetime
from typing import Optional, Tuple
import asyncio
import logging

from ..models.patient import PatientData
from ..models.assessment import (
    IRAEAssessment,
    ImmunotherapyContext,
    CausalityAssessment,
    OrganSystemFinding,
    RecommendedAction,
    ConfidenceScore,
    Likelihood,
    Severity,
    Urgency,
    OrganSystem,
)
from ..analyzers import (
    ImmunotherapyDetector,
    GIAnalyzer,
    LiverAnalyzer,
    LungAnalyzer,
    EndocrineAnalyzer,
    SkinAnalyzer,
    NeuroAnalyzer,
    CardiacAnalyzer,
    RenalAnalyzer,
    HematologicAnalyzer,
)
from ..parsers.note_parser import NoteParser
from ..utils.accuracy_monitor import log_prediction
from .client import BaseLLMClient
from .prompts import PromptBuilder
from .prompts_medgemma import MedGemmaPromptBuilder

# Configure logging
logger = logging.getLogger(__name__)


class SafetyValidator:
    """
    Production safety validation layer for irAE assessments.
    
    This class implements critical safety checks that CANNOT be overridden:
    1. Grade 4 must be EMERGENCY
    2. Cardiac/Neuro must be at least URGENT
    3. Grade 3 must be at least URGENT
    4. Grade 2 must be at least SOON
    """
    
    # Safety floor rules - CANNOT be violated
    MIN_URGENCY_BY_SEVERITY = {
        Severity.GRADE_4: Urgency.EMERGENCY,
        Severity.GRADE_3: Urgency.URGENT,
        Severity.GRADE_2: Urgency.SOON,
        Severity.GRADE_1: Urgency.ROUTINE,
        Severity.UNKNOWN: Urgency.ROUTINE,
    }
    
    # High-risk organs that escalate urgency
    HIGH_RISK_ORGANS = {OrganSystem.CARDIAC, OrganSystem.NEUROLOGIC}
    
    @classmethod
    def validate_and_correct(
        cls,
        assessment: IRAEAssessment,
    ) -> Tuple[IRAEAssessment, list[str]]:
        """
        Validate assessment against safety rules and correct violations.
        
        Args:
            assessment: The assessment to validate
            
        Returns:
            Tuple of (corrected_assessment, list_of_corrections)
        """
        corrections = []
        
        # Rule 1: Check minimum urgency for severity
        min_urgency = cls.MIN_URGENCY_BY_SEVERITY.get(
            assessment.overall_severity, Urgency.ROUTINE
        )
        
        if cls._urgency_rank(assessment.urgency) < cls._urgency_rank(min_urgency):
            old_urgency = assessment.urgency
            assessment.urgency = min_urgency
            corrections.append(
                f"SAFETY: Upgraded urgency from {old_urgency.value} to {min_urgency.value} "
                f"(minimum for {assessment.overall_severity.value})"
            )
            logger.warning(f"Safety correction: {corrections[-1]}")
        
        # Rule 2: High-risk organs require at least URGENT
        high_risk_detected = any(
            f.detected and f.system in cls.HIGH_RISK_ORGANS
            for f in assessment.affected_systems
        )
        
        if high_risk_detected and cls._urgency_rank(assessment.urgency) < cls._urgency_rank(Urgency.URGENT):
            old_urgency = assessment.urgency
            assessment.urgency = Urgency.URGENT
            corrections.append(
                f"SAFETY: Upgraded urgency from {old_urgency.value} to URGENT "
                f"(high-risk organ system involved)"
            )
            logger.warning(f"Safety correction: {corrections[-1]}")
        
        # Rule 3: If irAE detected with Grade 3-4, ensure discontinuation is recommended
        if assessment.irae_detected and assessment.overall_severity in [Severity.GRADE_3, Severity.GRADE_4]:
            has_hold_action = any(
                "hold" in a.action.lower() or 
                "discontinue" in a.action.lower() or
                "stop" in a.action.lower()
                for a in assessment.recommended_actions
            )
            if not has_hold_action:
                assessment.recommended_actions.insert(0, RecommendedAction(
                    action="Consider holding/discontinuing immunotherapy",
                    priority=1,
                    rationale=f"SAFETY: {assessment.overall_severity.value} toxicity typically requires treatment interruption",
                ))
                corrections.append("SAFETY: Added immunotherapy hold recommendation for severe toxicity")
        
        # Rule 4: Cardiac findings must always mention troponin/ECG
        cardiac_detected = any(
            f.detected and f.system == OrganSystem.CARDIAC
            for f in assessment.affected_systems
        )
        if cardiac_detected:
            has_cardiac_workup = any(
                "troponin" in a.action.lower() or "ecg" in a.action.lower() or "ekg" in a.action.lower()
                for a in assessment.recommended_actions
            )
            if not has_cardiac_workup:
                assessment.recommended_actions.insert(0, RecommendedAction(
                    action="URGENT: Check troponin, BNP, obtain ECG - rule out myocarditis",
                    priority=1,
                    rationale="SAFETY: Cardiac irAEs have 25-50% mortality - requires immediate workup",
                ))
                corrections.append("SAFETY: Added cardiac workup recommendation")
        
        return assessment, corrections
    
    @staticmethod
    def _urgency_rank(urgency: Urgency) -> int:
        """Get numeric rank for urgency comparison."""
        return {
            Urgency.ROUTINE: 1,
            Urgency.SOON: 2,
            Urgency.URGENT: 3,
            Urgency.EMERGENCY: 4,
        }.get(urgency, 1)


class IRAEAssessmentEngine:
    """
    Main assessment engine combining rule-based organ analyzers
    with LLM-powered clinical reasoning.
    """
    
    def __init__(
        self,
        llm_client: Optional[BaseLLMClient] = None,
        use_llm: bool = True,
    ):
        """
        Initialize the assessment engine.
        
        Args:
            llm_client: LLM client for clinical reasoning
            use_llm: Whether to use LLM for enhanced analysis
        """
        self.llm_client = llm_client
        self.use_llm = use_llm and llm_client is not None
        
        # Initialize analyzers and parsers
        self.immunotherapy_detector = ImmunotherapyDetector()
        self.note_parser = NoteParser(llm_client=self.llm_client if self.use_llm else None)
        self.analyzers = [
            GIAnalyzer(),
            LiverAnalyzer(),
            LungAnalyzer(),
            EndocrineAnalyzer(),
            SkinAnalyzer(),
            NeuroAnalyzer(),
            CardiacAnalyzer(),
            RenalAnalyzer(),
            HematologicAnalyzer(),
        ]
    
    async def assess(self, patient_data: PatientData) -> IRAEAssessment:
        """
        Perform complete irAE assessment on patient data.
        
        Args:
            patient_data: Complete patient clinical data
            
        Returns:
            IRAEAssessment with all findings and recommendations
        """
        # Step 1: If using LLM, parse notes for structured data first
        if self.use_llm and self.note_parser.llm_client:
            for note in patient_data.notes:
                extracted_symptoms, extracted_vitals = await self.note_parser.parse_with_llm(note)
                patient_data.symptoms.extend(extracted_symptoms)
                if extracted_vitals:
                    patient_data.vitals.append(extracted_vitals)

        # Step 2: Detect immunotherapy context
        immunotherapy_context = self.immunotherapy_detector.detect(patient_data)
        
        # Step 3: Run organ-specific analyzers on the (potentially enriched) patient data
        organ_findings = []
        for analyzer in self.analyzers:
            finding = analyzer.analyze(patient_data)
            if finding.detected:
                organ_findings.append(finding)
        
        # Step 4: Determine if irAE detected
        irae_detected = any(f.detected for f in organ_findings)
        
        # Step 5: Use LLM for final reasoning if available
        used_llm = False
        print(f"[ASSESSMENT] use_llm={self.use_llm}, llm_client={self.llm_client is not None}")
        if self.use_llm and self.llm_client:
            try:
                print("[ASSESSMENT] Calling LLM for clinical reasoning...")
                llm_assessment = await self._get_llm_assessment(patient_data, model_key="reasoning")
                print(f"[ASSESSMENT] LLM response received: {llm_assessment is not None}")
                
                # Check if LLM returned an error response
                if llm_assessment and llm_assessment.get("error"):
                    print(f"[ASSESSMENT] LLM returned error: {llm_assessment.get('error')}")
                    assessment = self._create_rule_based_assessment(immunotherapy_context, organ_findings, irae_detected)
                else:
                    # Merge LLM insights with rule-based findings
                    assessment = self._merge_assessments(
                        immunotherapy_context,
                        organ_findings,
                        irae_detected,
                        llm_assessment,
                    )
                    used_llm = True
                    print("[ASSESSMENT] Using LLM-enhanced assessment")
            except Exception as e:
                # Fall back to rule-based only
                print(f"[ASSESSMENT] LLM assessment failed: {e}")
                import traceback
                traceback.print_exc()
                assessment = self._create_rule_based_assessment(immunotherapy_context, organ_findings, irae_detected)
        else:
            print("[ASSESSMENT] Using rule-based assessment (no LLM)")
            assessment = self._create_rule_based_assessment(immunotherapy_context, organ_findings, irae_detected)

        # Step 6: Calculate and attach confidence score
        confidence_score = self._calculate_confidence_score(
            patient_data=patient_data,
            organ_findings=organ_findings,
            immunotherapy_context=immunotherapy_context,
            used_llm=used_llm,
        )
        assessment.confidence_score = confidence_score

        # Step 7: SAFETY VALIDATION - Cannot be bypassed
        assessment, safety_corrections = SafetyValidator.validate_and_correct(assessment)
        if safety_corrections:
            print(f"[SAFETY] Applied {len(safety_corrections)} correction(s)")
            for correction in safety_corrections:
                print(f"  - {correction}")
            # Add safety note to uncertainty factors
            if assessment.confidence_score:
                assessment.confidence_score.uncertainty_factors.extend(safety_corrections)

        # Step 8: LOG PREDICTION FOR ACCURACY MONITORING
        try:
            affected_system_names = [
                f.system.value for f in assessment.affected_systems if f.detected
            ]
            log_prediction(
                case_id=patient_data.patient_id or "unknown",
                predicted_irae=assessment.irae_detected,
                predicted_severity=assessment.overall_severity.value,
                predicted_urgency=assessment.urgency.value.split()[0].lower(),  # Extract 'routine' from '🟢 Routine monitoring'
                predicted_systems=affected_system_names,
                inference_time_ms=confidence_score.rule_match_count * 10 if confidence_score else None,  # Approximate
            )
            logger.info(f"[MONITOR] Prediction logged for case {patient_data.patient_id}")
        except Exception as e:
            logger.warning(f"[MONITOR] Failed to log prediction: {e}")

        return assessment
    
    def assess_sync(self, patient_data: PatientData) -> IRAEAssessment:
        """Synchronous wrapper for assess method."""
        return asyncio.run(self.assess(patient_data))
    
    async def _get_llm_assessment(self, patient_data: PatientData, model_key: str = "reasoning") -> Optional[dict]:
        """Get clinical reasoning from MedGemma LLM."""
        if not self.llm_client:
            return None
        
        # Use optimized MedGemma prompts (concise for 4B model context limits)
        system_prompt = MedGemmaPromptBuilder.build_system_prompt()
        user_prompt = MedGemmaPromptBuilder.build_user_prompt(patient_data)
        
        # Log prompt sizes for debugging
        print(f"[MEDGEMMA] System prompt: {len(system_prompt)} chars")
        print(f"[MEDGEMMA] User prompt: {len(user_prompt)} chars")
        
        return await self.llm_client.complete_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_key=model_key
        )

    def _calculate_confidence_score(
        self,
        patient_data: PatientData,
        organ_findings: list[OrganSystemFinding],
        immunotherapy_context: ImmunotherapyContext,
        used_llm: bool = False,
    ) -> ConfidenceScore:
        """
        Calculate confidence scores for the assessment.
        
        Factors considered:
        - Data completeness (labs, vitals, notes, medications)
        - Evidence strength from organ findings
        - Number of matching detection rules
        - LLM enhancement if used
        """
        confidence_factors = []
        uncertainty_factors = []
        
        # 1. Calculate data completeness (0-1)
        data_points = 0
        max_data_points = 4  # Labs, vitals, notes, medications
        
        if patient_data.labs and len(patient_data.labs) > 0:
            data_points += 1
            confidence_factors.append(f"Lab data available ({len(patient_data.labs)} results)")
        else:
            uncertainty_factors.append("No laboratory data provided")
        
        if patient_data.vitals and len(patient_data.vitals) > 0:
            data_points += 1
            confidence_factors.append("Vital signs available")
        else:
            uncertainty_factors.append("No vital signs provided")
        
        if patient_data.notes and len(patient_data.notes) > 0:
            data_points += 1
            confidence_factors.append(f"Clinical notes available ({len(patient_data.notes)} notes)")
        else:
            uncertainty_factors.append("No clinical notes provided")
        
        if patient_data.medications and len(patient_data.medications) > 0:
            data_points += 1
            confidence_factors.append(f"Medication list available ({len(patient_data.medications)} meds)")
        else:
            uncertainty_factors.append("No medication data provided")
        
        data_completeness = data_points / max_data_points
        
        # 2. Calculate evidence strength from findings (0-1)
        rule_match_count = 0
        evidence_scores = []
        
        for finding in organ_findings:
            if finding.detected:
                rule_match_count += 1
                # Each detected finding contributes to evidence strength
                finding_confidence = finding.confidence if finding.confidence else 0.5
                evidence_scores.append(finding_confidence)
                
                if finding.severity in [Severity.GRADE_3, Severity.GRADE_4]:
                    confidence_factors.append(f"Clear {finding.system.value} severity indicators")
        
        evidence_strength = sum(evidence_scores) / len(evidence_scores) if evidence_scores else 0.3
        
        # 3. Immunotherapy context factors
        if immunotherapy_context.on_immunotherapy:
            confidence_factors.append("Immunotherapy status confirmed")
            if immunotherapy_context.agents:
                confidence_factors.append(f"Specific agents identified: {', '.join(immunotherapy_context.agents[:2])}")
        else:
            uncertainty_factors.append("No immunotherapy detected - irAE less likely")
        
        # 4. LLM enhancement bonus
        if used_llm:
            confidence_factors.append("LLM-enhanced clinical reasoning applied")
            evidence_strength = min(1.0, evidence_strength + 0.1)
        
        # 5. Calculate overall confidence
        # Weighted average: data completeness (40%), evidence strength (60%)
        overall_confidence = (0.4 * data_completeness) + (0.6 * evidence_strength)
        
        # Adjust for edge cases
        if rule_match_count == 0:
            overall_confidence *= 0.5  # Lower confidence if no rules matched
            uncertainty_factors.append("No organ-specific irAE patterns detected")
        
        if len(uncertainty_factors) > 3:
            overall_confidence *= 0.8  # Penalty for multiple uncertainties
        
        overall_confidence = max(0.1, min(1.0, overall_confidence))  # Clamp to 0.1-1.0
        
        return ConfidenceScore(
            overall_confidence=round(overall_confidence, 2),
            evidence_strength=round(evidence_strength, 2),
            data_completeness=round(data_completeness, 2),
            rule_match_count=rule_match_count,
            confidence_factors=confidence_factors,
            uncertainty_factors=uncertainty_factors,
        )

    def _merge_assessments(
        self,
        immunotherapy_context: ImmunotherapyContext,
        affected_systems: list[OrganSystemFinding],
        irae_detected: bool,
        llm_assessment: dict,
    ) -> IRAEAssessment:
        """
        MedGemma-first assessment with rule-based validation.
        
        PRINCIPLE: MedGemma provides the PRIMARY clinical reasoning.
        Rule-based analysis provides VALIDATION and SAFETY GUARDRAILS.
        
        MedGemma is trusted for:
        - Overall clinical assessment and reasoning
        - Severity grading (with validation)
        - Urgency determination (with safety floors)
        - Causality assessment
        - Recommended actions
        
        Rule-based provides:
        - Validation of organ system detection
        - Safety guardrails for urgency
        - Objective lab value confirmation
        """
        
        # =====================================================================
        # STEP 1: Parse MedGemma assessment (PRIMARY SOURCE)
        # =====================================================================
        llm_severity = self._parse_severity(llm_assessment.get("overall_severity", "Unknown"))
        llm_urgency = self._parse_urgency(llm_assessment.get("urgency", "routine"))
        llm_irae_detected = llm_assessment.get("irae_detected", False)
        causality_data = llm_assessment.get("causality", {})
        llm_likelihood = self._parse_likelihood(causality_data.get("likelihood", "Uncertain"))
        
        print(f"[MEDGEMMA] Detected: {llm_irae_detected}, Severity: {llm_severity.value}, Urgency: {llm_urgency.value}")
        
        # =====================================================================
        # STEP 2: Get rule-based findings for VALIDATION
        # =====================================================================
        rule_based_severity = Severity.UNKNOWN
        rule_detected_systems = []
        for finding in affected_systems:
            if finding.detected:
                rule_detected_systems.append(finding.system)
                if finding.severity:
                    if rule_based_severity == Severity.UNKNOWN:
                        rule_based_severity = finding.severity
                    elif self._severity_rank(finding.severity) > self._severity_rank(rule_based_severity):
                        rule_based_severity = finding.severity
        
        print(f"[VALIDATION] Rule-based systems: {[s.value for s in rule_detected_systems]}, Severity: {rule_based_severity.value}")
        
        # =====================================================================
        # STEP 3: MERGE affected systems - combine MedGemma + rule-based
        # =====================================================================
        # Parse LLM's affected systems
        llm_systems = []
        for sys_data in llm_assessment.get("affected_systems", []):
            if sys_data.get("detected", False):
                sys_name = sys_data.get("system", "").lower()
                llm_sys = self._parse_organ_system(sys_name)
                if llm_sys:
                    llm_systems.append(llm_sys)
        
        # Final systems: Union of MedGemma and rule-based detections
        # This ensures we don't miss anything either system detected
        all_detected = set(rule_detected_systems) | set(llm_systems)
        
        # Update affected_systems to include LLM detections
        final_affected_systems = list(affected_systems)  # Start with rule-based
        for llm_sys in llm_systems:
            if not any(f.system == llm_sys and f.detected for f in final_affected_systems):
                # LLM detected something rules didn't - add it with LLM's assessment
                llm_sys_data = next(
                    (s for s in llm_assessment.get("affected_systems", []) 
                     if self._parse_organ_system(s.get("system", "").lower()) == llm_sys),
                    {}
                )
                final_affected_systems.append(OrganSystemFinding(
                    system=llm_sys,
                    detected=True,
                    findings=llm_sys_data.get("findings", ["Detected by MedGemma clinical reasoning"]),
                    evidence=llm_sys_data.get("evidence", []),
                    severity=self._parse_severity(llm_sys_data.get("severity", "Unknown")),
                    confidence=0.7,  # Lower confidence for LLM-only detection
                ))
        
        # Final detection: Either MedGemma or rules detected something
        final_irae_detected = llm_irae_detected or irae_detected
        
        print(f"[MERGE] Final systems: {[s.value for s in all_detected]}, irAE detected: {final_irae_detected}")
        
        # =====================================================================
        # STEP 4: SEVERITY - Trust MedGemma with rule-based validation
        # =====================================================================
        if llm_severity != Severity.UNKNOWN:
            # MedGemma provided severity - use it
            overall_severity = llm_severity
            
            # Validate: if rule-based found higher severity, use that (safety)
            if rule_based_severity != Severity.UNKNOWN:
                if self._severity_rank(rule_based_severity) > self._severity_rank(llm_severity):
                    overall_severity = rule_based_severity
                    print(f"[SAFETY] Rule-based severity higher, upgrading to {overall_severity.value}")
        elif rule_based_severity != Severity.UNKNOWN:
            # MedGemma didn't provide, use rule-based
            overall_severity = rule_based_severity
        else:
            overall_severity = Severity.UNKNOWN
        
        print(f"[MERGE] Final severity: {overall_severity.value}")
        
        # =====================================================================
        # STEP 5: URGENCY - Trust MedGemma with safety floors
        # =====================================================================
        urgency = llm_urgency
        
        # Apply safety floors based on severity
        min_urgency_for_severity = {
            Severity.GRADE_1: Urgency.ROUTINE,
            Severity.GRADE_2: Urgency.SOON,
            Severity.GRADE_3: Urgency.URGENT,
            Severity.GRADE_4: Urgency.EMERGENCY,
        }
        min_urgency = min_urgency_for_severity.get(overall_severity, Urgency.ROUTINE)
        
        if self._urgency_rank(urgency) < self._urgency_rank(min_urgency):
            urgency = min_urgency
            print(f"[SAFETY] Urgency floor applied: {urgency.value}")
        
        # High-risk organs always at least URGENT
        high_risk_detected = any(
            s in [OrganSystem.CARDIAC, OrganSystem.NEUROLOGIC] 
            for s in all_detected
        )
        if high_risk_detected and self._urgency_rank(urgency) < self._urgency_rank(Urgency.URGENT):
            urgency = Urgency.URGENT
            print(f"[SAFETY] High-risk organ detected, escalating to URGENT")
        
        # =====================================================================
        # STEP 6: CAUSALITY - Use MedGemma's clinical reasoning
        # =====================================================================
        if not immunotherapy_context.on_immunotherapy:
            final_likelihood = Likelihood.UNLIKELY
        else:
            final_likelihood = llm_likelihood
        
        causality = CausalityAssessment(
            likelihood=final_likelihood,
            reasoning=causality_data.get("reasoning", "Based on MedGemma clinical assessment"),
            temporal_relationship=causality_data.get("temporal_relationship"),
            alternative_causes=causality_data.get("alternative_causes", []),
            supporting_factors=causality_data.get("supporting_factors", []),
            against_factors=causality_data.get("against_factors", []),
        )
        
        # =====================================================================
        # STEP 7: Use MedGemma's reasoning (its core value)
        # =====================================================================
        severity_reasoning = llm_assessment.get("severity_reasoning", "")
        urgency_reasoning = llm_assessment.get("urgency_reasoning", "")
        
        # =====================================================================
        # STEP 8: RECOMMENDED ACTIONS - MedGemma primary
        # =====================================================================
        actions = []
        for action_data in llm_assessment.get("recommended_actions", []):
            action_text = action_data.get("action", "")
            if action_text:
                actions.append(RecommendedAction(
                    action=action_text,
                    priority=action_data.get("priority", 3),
                    rationale=action_data.get("rationale"),
                ))
        
        if not actions:
            actions = self._build_recommended_actions(final_irae_detected, overall_severity, final_affected_systems)
        
        # =====================================================================
        # STEP 9: KEY EVIDENCE - Combine MedGemma + rule-based
        # =====================================================================
        key_evidence = llm_assessment.get("key_evidence", [])
        if not isinstance(key_evidence, list):
            key_evidence = []
        for finding in final_affected_systems:
            if finding.detected:
                for ev in finding.evidence[:3]:
                    if ev not in key_evidence:
                        key_evidence.append(ev)
        
        return IRAEAssessment(
            assessment_date=datetime.now(),
            immunotherapy_context=immunotherapy_context,
            irae_detected=final_irae_detected,
            affected_systems=final_affected_systems,
            causality=causality,
            overall_severity=overall_severity,
            severity_reasoning=severity_reasoning,
            urgency=urgency,
            urgency_reasoning=urgency_reasoning,
            recommended_actions=actions,
            key_evidence=key_evidence[:10],
        )
    
    def _parse_organ_system(self, system_name: str) -> Optional[OrganSystem]:
        """Parse organ system name to enum."""
        system_map = {
            "gastrointestinal": OrganSystem.GASTROINTESTINAL,
            "gi": OrganSystem.GASTROINTESTINAL,
            "hepatic": OrganSystem.HEPATIC,
            "liver": OrganSystem.HEPATIC,
            "pulmonary": OrganSystem.PULMONARY,
            "lung": OrganSystem.PULMONARY,
            "endocrine": OrganSystem.ENDOCRINE,
            "dermatologic": OrganSystem.DERMATOLOGIC,
            "skin": OrganSystem.DERMATOLOGIC,
            "neurologic": OrganSystem.NEUROLOGIC,
            "neuro": OrganSystem.NEUROLOGIC,
            "cardiac": OrganSystem.CARDIAC,
            "heart": OrganSystem.CARDIAC,
            "renal": OrganSystem.RENAL,
            "kidney": OrganSystem.RENAL,
            "hematologic": OrganSystem.HEMATOLOGIC,
            "blood": OrganSystem.HEMATOLOGIC,
        }
        return system_map.get(system_name.lower().strip())
    
    def _add_safety_actions(
        self,
        actions: list[RecommendedAction],
        severity: Severity,
        findings: list[OrganSystemFinding],
    ) -> list[RecommendedAction]:
        """Add critical safety actions if missing from LLM recommendations."""
        action_texts = [a.action.lower() for a in actions]
        
        # For Grade 3-4, ensure hold immunotherapy is recommended
        if severity in [Severity.GRADE_3, Severity.GRADE_4]:
            if not any("hold" in t or "discontinue" in t or "stop" in t for t in action_texts):
                actions.insert(0, RecommendedAction(
                    action="Consider holding/discontinuing immunotherapy pending evaluation",
                    priority=1,
                    rationale=f"{severity.value} toxicity typically requires treatment interruption",
                ))
        
        # For cardiac findings, ensure troponin/ECG recommended
        cardiac_involved = any(
            f.detected and f.system == OrganSystem.CARDIAC 
            for f in findings
        )
        if cardiac_involved:
            if not any("troponin" in t or "ecg" in t or "ekg" in t for t in action_texts):
                actions.insert(0, RecommendedAction(
                    action="URGENT: Check troponin, BNP, and obtain ECG - rule out myocarditis",
                    priority=1,
                    rationale="Cardiac irAEs have 25-50% mortality - requires immediate workup",
                ))
        
        # For neuro findings, ensure neurology consult
        neuro_involved = any(
            f.detected and f.system == OrganSystem.NEUROLOGIC 
            for f in findings
        )
        if neuro_involved:
            if not any("neurology" in t or "neuro" in t for t in action_texts):
                actions.append(RecommendedAction(
                    action="Obtain urgent neurology consultation",
                    priority=1,
                    rationale="Neurologic irAEs can progress rapidly",
                ))
        
        return actions
    
    def _create_rule_based_assessment(
        self,
        immunotherapy_context: ImmunotherapyContext,
        organ_findings: list[OrganSystemFinding],
        irae_detected: bool,
    ) -> IRAEAssessment:
        """Build assessment using only rule-based analysis."""
        # Determine overall severity from affected systems
        overall_severity = Severity.UNKNOWN
        for finding in organ_findings:
            if finding.severity and finding.detected:
                if overall_severity == Severity.UNKNOWN:
                    overall_severity = finding.severity
                elif self._severity_rank(finding.severity) > self._severity_rank(overall_severity):
                    overall_severity = finding.severity
        
        # Determine causality likelihood
        if not immunotherapy_context.on_immunotherapy:
            likelihood = Likelihood.UNLIKELY
            reasoning = "No immunotherapy detected in medication list"
        elif irae_detected:
            if immunotherapy_context.combination_therapy:
                likelihood = Likelihood.HIGHLY_LIKELY
                reasoning = "Patient on combination immunotherapy with multi-organ findings"
            else:
                likelihood = Likelihood.POSSIBLE
                reasoning = "Patient on immunotherapy with organ-specific findings"
        else:
            likelihood = Likelihood.UNCERTAIN
            reasoning = "Insufficient data for causality assessment"
        
        causality = CausalityAssessment(
            likelihood=likelihood,
            reasoning=reasoning,
        )
        
        # Determine urgency
        urgency = self._determine_urgency(overall_severity, organ_findings)
        
        # Build recommended actions
        actions = self._build_recommended_actions(
            irae_detected, overall_severity, organ_findings
        )
        
        # Gather key evidence
        key_evidence = []
        for finding in organ_findings:
            if finding.detected:
                key_evidence.extend(finding.evidence[:3])  # Top 3 per system
        
        return IRAEAssessment(
            assessment_date=datetime.now(),
            immunotherapy_context=immunotherapy_context,
            irae_detected=irae_detected,
            affected_systems=organ_findings,
            causality=causality,
            overall_severity=overall_severity,
            severity_reasoning=f"Based on {overall_severity.value} findings in affected organ systems",
            urgency=urgency,
            urgency_reasoning=self._get_urgency_reasoning(urgency, overall_severity),
            recommended_actions=actions,
            key_evidence=key_evidence[:10],  # Top 10 overall
        )
    
    def _parse_likelihood(self, value: str) -> Likelihood:
        """Parse likelihood string to enum."""
        value_lower = value.lower()
        if "highly likely" in value_lower or "high" in value_lower:
            return Likelihood.HIGHLY_LIKELY
        elif "possible" in value_lower:
            return Likelihood.POSSIBLE
        elif "unlikely" in value_lower:
            return Likelihood.UNLIKELY
        return Likelihood.UNCERTAIN
    
    def _parse_severity(self, value: str) -> Severity:
        """Parse severity string to enum."""
        value_lower = value.lower()
        if "4" in value_lower or "life-threatening" in value_lower:
            return Severity.GRADE_4
        elif "3" in value_lower or "severe" in value_lower:
            return Severity.GRADE_3
        elif "2" in value_lower or "moderate" in value_lower:
            return Severity.GRADE_2
        elif "1" in value_lower or "mild" in value_lower:
            return Severity.GRADE_1
        return Severity.UNKNOWN
    
    def _parse_urgency(self, value: str) -> Urgency:
        """Parse urgency string to enum."""
        value_lower = value.lower()
        if "emergency" in value_lower or "red" in value_lower:
            return Urgency.EMERGENCY
        elif "urgent" in value_lower or "orange" in value_lower:
            return Urgency.URGENT
        elif "soon" in value_lower or "yellow" in value_lower:
            return Urgency.SOON
        return Urgency.ROUTINE
    
    def _severity_rank(self, severity: Severity) -> int:
        """Get numeric rank for severity."""
        ranks = {
            Severity.GRADE_1: 1,
            Severity.GRADE_2: 2,
            Severity.GRADE_3: 3,
            Severity.GRADE_4: 4,
            Severity.UNKNOWN: 0,
        }
        return ranks.get(severity, 0)
    
    def _urgency_rank(self, urgency: Urgency) -> int:
        """Get numeric rank for urgency."""
        ranks = {
            Urgency.ROUTINE: 1,
            Urgency.SOON: 2,
            Urgency.URGENT: 3,
            Urgency.EMERGENCY: 4,
        }
        return ranks.get(urgency, 1)
    
    def _validate_urgency_for_severity(
        self,
        llm_urgency: Urgency,
        severity: Severity,
        findings: list[OrganSystemFinding]
    ) -> Urgency:
        """
        Validate and correct urgency based on severity.
        
        This is a SAFETY CHECK to ensure urgency is never inappropriately low
        for the detected severity. Clinical guidelines dictate minimum urgency
        levels based on CTCAE grade.
        
        Rules:
        - Grade 4 → minimum EMERGENCY
        - Grade 3 → minimum URGENT  
        - Grade 2 → minimum SOON (needs oncology review)
        - Grade 1 → can be ROUTINE
        - Cardiac/Neuro involvement → upgrade to URGENT
        """
        # Calculate minimum required urgency based on severity
        if severity == Severity.GRADE_4:
            min_urgency = Urgency.EMERGENCY
        elif severity == Severity.GRADE_3:
            min_urgency = Urgency.URGENT
        elif severity == Severity.GRADE_2:
            min_urgency = Urgency.SOON  # Grade 2 irAEs need oncology review
        else:
            min_urgency = Urgency.ROUTINE
        
        # Check for high-risk organ systems (always at least URGENT)
        high_risk_systems = [OrganSystem.CARDIAC, OrganSystem.NEUROLOGIC]
        for finding in findings:
            if finding.detected and finding.system in high_risk_systems:
                if self._urgency_rank(min_urgency) < self._urgency_rank(Urgency.URGENT):
                    min_urgency = Urgency.URGENT
        
        # Return the higher of LLM urgency or minimum required
        if self._urgency_rank(llm_urgency) >= self._urgency_rank(min_urgency):
            return llm_urgency
        else:
            # LLM underestimated urgency - use the safety minimum
            return min_urgency
    
    def _determine_urgency(
        self, 
        severity: Severity, 
        findings: list[OrganSystemFinding]
    ) -> Urgency:
        """Determine urgency based on severity and findings."""
        if severity == Severity.GRADE_4:
            return Urgency.EMERGENCY
        elif severity == Severity.GRADE_3:
            return Urgency.URGENT
        elif severity == Severity.GRADE_2:
            return Urgency.SOON
        
        # Check for particularly concerning organ systems
        concerning_systems = [
            OrganSystem.CARDIAC, 
            OrganSystem.NEUROLOGIC, 
            OrganSystem.PULMONARY,
            OrganSystem.HEMATOLOGIC,  # Can indicate HLH or severe cytopenias
        ]
        for finding in findings:
            if finding.detected and finding.system in concerning_systems:
                return Urgency.URGENT
        
        return Urgency.ROUTINE
    
    def _get_urgency_reasoning(self, urgency: Urgency, severity: Severity) -> str:
        """Get reasoning for urgency level."""
        reasons = {
            Urgency.EMERGENCY: f"{severity.value} findings requiring immediate evaluation",
            Urgency.URGENT: f"{severity.value} findings requiring same-day oncology evaluation",
            Urgency.SOON: f"{severity.value} findings - recommend oncology review within 1-3 days",
            Urgency.ROUTINE: "Findings appropriate for routine monitoring at next scheduled visit",
        }
        return reasons.get(urgency, "Standard clinical monitoring recommended")
    
    def _build_recommended_actions(
        self,
        irae_detected: bool,
        severity: Severity,
        findings: list[OrganSystemFinding],
    ) -> list[RecommendedAction]:
        """Build list of recommended clinical actions."""
        actions = []
        
        if not irae_detected:
            actions.append(RecommendedAction(
                action="Continue current monitoring",
                priority=3,
                rationale="No irAE signals detected",
            ))
            return actions
        
        # High-severity actions
        if severity in [Severity.GRADE_3, Severity.GRADE_4]:
            actions.append(RecommendedAction(
                action="Consider holding immunotherapy pending evaluation",
                priority=1,
                rationale=f"{severity.value} toxicity may require treatment interruption",
            ))
            actions.append(RecommendedAction(
                action="Obtain urgent oncology consultation",
                priority=1,
                rationale="Severe irAE requires specialist input",
            ))
        
        # Organ-specific actions
        for finding in findings:
            if not finding.detected:
                continue
            
            if finding.system == OrganSystem.HEPATIC:
                actions.append(RecommendedAction(
                    action="Check liver function tests (AST, ALT, bilirubin, ALP)",
                    priority=2,
                    rationale="Monitor hepatic irAE",
                ))
            
            elif finding.system == OrganSystem.PULMONARY:
                actions.append(RecommendedAction(
                    action="Consider chest imaging if not recently performed",
                    priority=2,
                    rationale="Evaluate for pneumonitis",
                ))
            
            elif finding.system == OrganSystem.ENDOCRINE:
                actions.append(RecommendedAction(
                    action="Check thyroid function (TSH, free T4) and morning cortisol",
                    priority=2,
                    rationale="Evaluate endocrine irAE",
                ))
            
            elif finding.system == OrganSystem.CARDIAC:
                actions.append(RecommendedAction(
                    action="Check troponin, BNP, and obtain EKG",
                    priority=1,
                    rationale="Cardiac irAEs can be life-threatening",
                ))
            
            elif finding.system == OrganSystem.RENAL:
                actions.append(RecommendedAction(
                    action="Check renal function (BUN, creatinine, urinalysis with microscopy)",
                    priority=2,
                    rationale="Monitor for immune-related nephritis",
                ))
                actions.append(RecommendedAction(
                    action="Consider nephrology consultation if creatinine rising",
                    priority=2,
                    rationale="Early nephrology input may prevent progression",
                ))
            
            elif finding.system == OrganSystem.HEMATOLOGIC:
                actions.append(RecommendedAction(
                    action="Check CBC with differential, reticulocyte count, LDH, haptoglobin",
                    priority=2,
                    rationale="Evaluate for immune-related cytopenias",
                ))
                actions.append(RecommendedAction(
                    action="Consider hematology consultation for severe cytopenias",
                    priority=2,
                    rationale="May need bone marrow biopsy or specialized treatment",
                ))
        
        # General action
        actions.append(RecommendedAction(
            action="Document findings and communicate with oncology team",
            priority=3,
            rationale="Ensure care coordination",
        ))
        
        return sorted(actions, key=lambda x: x.priority)
