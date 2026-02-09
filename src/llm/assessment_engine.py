"""irAE Assessment Engine combining rule-based and LLM analysis."""

from datetime import datetime
from typing import Optional
import asyncio

from ..models.patient import PatientData
from ..models.assessment import (
    IRAEAssessment,
    ImmunotherapyContext,
    CausalityAssessment,
    OrganSystemFinding,
    RecommendedAction,
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
)
from ..parsers.note_parser import NoteParser
from .client import BaseLLMClient
from .prompts import PromptBuilder


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
        print(f"[ASSESSMENT] use_llm={self.use_llm}, llm_client={self.llm_client is not None}")
        if self.use_llm and self.llm_client:
            try:
                print("[ASSESSMENT] Calling LLM for clinical reasoning...")
                llm_assessment = await self._get_llm_assessment(patient_data, model_key="reasoning")
                print(f"[ASSESSMENT] LLM response received: {llm_assessment is not None}")
                # Merge LLM insights with rule-based findings
                assessment = self._merge_assessments(
                    immunotherapy_context,
                    organ_findings,
                    irae_detected,
                    llm_assessment,
                )
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

        return assessment
    
    def assess_sync(self, patient_data: PatientData) -> IRAEAssessment:
        """Synchronous wrapper for assess method."""
        return asyncio.run(self.assess(patient_data))
    
    async def _get_llm_assessment(self, patient_data: PatientData, model_key: str = "reasoning") -> Optional[dict]:
        """Get clinical reasoning from LLM."""
        if not self.llm_client:
            return None
        
        # PromptBuilder uses static methods
        system_prompt = PromptBuilder.build_full_system_prompt(include_json_schema=True)
        user_prompt = PromptBuilder.build_assessment_prompt(patient_data)
        
        return await self.llm_client.complete_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_key=model_key
        )

    def _merge_assessments(
        self,
        immunotherapy_context: ImmunotherapyContext,
        affected_systems: list[OrganSystemFinding],
        irae_detected: bool,
        llm_assessment: dict,
    ) -> IRAEAssessment:
        """Merge rule-based and LLM assessments."""
        # Parse LLM causality
        causality_data = llm_assessment.get("causality", {})
        causality = CausalityAssessment(
            likelihood=self._parse_likelihood(causality_data.get("likelihood", "Uncertain")),
            reasoning=causality_data.get("reasoning", "Based on available clinical data"),
            temporal_relationship=causality_data.get("temporal_relationship"),
            alternative_causes=causality_data.get("alternative_causes", []),
            supporting_factors=causality_data.get("supporting_factors", []),
            against_factors=causality_data.get("against_factors", []),
        )
        
        # Parse severity
        overall_severity = self._parse_severity(
            llm_assessment.get("overall_severity", "Unknown")
        )
        
        # Parse urgency
        urgency = self._parse_urgency(llm_assessment.get("urgency", "routine"))
        
        # Parse recommended actions
        actions = []
        for action_data in llm_assessment.get("recommended_actions", []):
            actions.append(RecommendedAction(
                action=action_data.get("action", ""),
                priority=action_data.get("priority", 3),
                rationale=action_data.get("rationale"),
            ))
        
        # Use LLM's irAE detection if it found something we missed
        irae_detected = irae_detected or llm_assessment.get("irae_detected", False)
        
        return IRAEAssessment(
            assessment_date=datetime.now(),
            immunotherapy_context=immunotherapy_context,
            irae_detected=irae_detected,
            affected_systems=affected_systems,
            causality=causality,
            overall_severity=overall_severity,
            severity_reasoning=llm_assessment.get("severity_reasoning", ""),
            urgency=urgency,
            urgency_reasoning=llm_assessment.get("urgency_reasoning", ""),
            recommended_actions=actions,
            key_evidence=llm_assessment.get("key_evidence", []),
        )
    
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
        concerning_systems = [OrganSystem.CARDIAC, OrganSystem.NEUROLOGIC, OrganSystem.PULMONARY]
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
        
        # General action
        actions.append(RecommendedAction(
            action="Document findings and communicate with oncology team",
            priority=3,
            rationale="Ensure care coordination",
        ))
        
        return sorted(actions, key=lambda x: x.priority)
