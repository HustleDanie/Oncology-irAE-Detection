"""Output formatting utilities for irAE assessments."""

from ..models.assessment import IRAEAssessment, Urgency


def format_assessment_output(assessment: IRAEAssessment) -> str:
    """
    Format an irAE assessment into the structured output format.
    
    Args:
        assessment: The completed irAE assessment
        
    Returns:
        Formatted string output following the clinical output template
    """
    output_lines = []
    
    # Header
    output_lines.append("=" * 60)
    output_lines.append("IMMUNE-RELATED ADVERSE EVENT (irAE) ASSESSMENT")
    output_lines.append("=" * 60)
    output_lines.append("")
    
    # Immunotherapy Context
    output_lines.append("IMMUNOTHERAPY CONTEXT:")
    ctx = assessment.immunotherapy_context
    if ctx.on_immunotherapy:
        agents = ", ".join(ctx.agents) if ctx.agents else "Unknown agent"
        classes = ", ".join(ctx.drug_classes) if ctx.drug_classes else "Unknown class"
        output_lines.append(f"  Patient is on immunotherapy: {agents}")
        output_lines.append(f"  Drug class(es): {classes}")
        if ctx.combination_therapy:
            output_lines.append("  ⚠️  Combination immunotherapy (higher irAE risk)")
        if ctx.most_recent_dose:
            output_lines.append(f"  Most recent dose: {ctx.most_recent_dose.strftime('%Y-%m-%d')}")
        if ctx.duration_on_therapy:
            output_lines.append(f"  Duration on therapy: {ctx.duration_on_therapy}")
    else:
        output_lines.append("  No active immunotherapy detected")
        output_lines.append("  (irAE likelihood is lower but not excluded)")
    output_lines.append("")
    
    # irAE Detection Result
    output_lines.append("POSSIBLE irAE DETECTED:")
    if assessment.irae_detected:
        output_lines.append("  ✓ YES - Possible irAE signals identified")
    else:
        output_lines.append("  ✗ NO - No clear irAE signals detected")
    output_lines.append("")
    
    # Affected Organ Systems
    output_lines.append("AFFECTED ORGAN SYSTEM(S):")
    affected = [f for f in assessment.affected_systems if f.detected]
    if affected:
        for finding in affected:
            output_lines.append(f"  • {finding.system.value}:")
            for f in finding.findings:
                output_lines.append(f"      - {f}")
            if finding.evidence:
                output_lines.append("      Evidence:")
                for e in finding.evidence:
                    output_lines.append(f"        → {e}")
            if finding.severity:
                output_lines.append(f"      Severity: {finding.severity.value}")
    else:
        output_lines.append("  None identified")
    output_lines.append("")
    
    # Likelihood Assessment
    output_lines.append("LIKELIHOOD THIS IS AN irAE:")
    output_lines.append(f"  {assessment.causality.likelihood.value}")
    output_lines.append(f"  Reasoning: {assessment.causality.reasoning}")
    if assessment.causality.temporal_relationship:
        output_lines.append(f"  Temporal relationship: {assessment.causality.temporal_relationship}")
    if assessment.causality.alternative_causes:
        output_lines.append("  Alternative causes considered:")
        for cause in assessment.causality.alternative_causes:
            output_lines.append(f"    - {cause}")
    output_lines.append("")
    
    # Severity Assessment
    output_lines.append("SEVERITY (CTCAE-style estimate):")
    output_lines.append(f"  {assessment.overall_severity.value}")
    output_lines.append(f"  Reasoning: {assessment.severity_reasoning}")
    output_lines.append("")
    
    # Urgency Triage
    output_lines.append("URGENCY TRIAGE:")
    output_lines.append(f"  {assessment.urgency.value}")
    output_lines.append(f"  Why: {assessment.urgency_reasoning}")
    output_lines.append("")
    
    # Recommended Actions
    output_lines.append("RECOMMENDED NEXT CLINICAL STEPS:")
    if assessment.recommended_actions:
        for action in sorted(assessment.recommended_actions, key=lambda x: x.priority):
            output_lines.append(f"  {action.priority}. {action.action}")
            if action.rationale:
                output_lines.append(f"     ({action.rationale})")
    else:
        output_lines.append("  • Continue current monitoring")
    output_lines.append("")
    
    # Key Supporting Data
    output_lines.append("KEY SUPPORTING DATA:")
    if assessment.key_evidence:
        for evidence in assessment.key_evidence:
            output_lines.append(f"  • {evidence}")
    else:
        output_lines.append("  No specific data points highlighted")
    output_lines.append("")
    
    # Disclaimer
    output_lines.append("-" * 60)
    output_lines.append("⚠️  IMPORTANT DISCLAIMER:")
    output_lines.append(f"  {assessment.disclaimer}")
    output_lines.append("-" * 60)
    
    return "\n".join(output_lines)


def format_urgency_badge(urgency: Urgency) -> str:
    """Format urgency as a colored badge for display."""
    badges = {
        Urgency.ROUTINE: "🟢 ROUTINE",
        Urgency.SOON: "🟡 SOON",
        Urgency.URGENT: "🟠 URGENT",
        Urgency.EMERGENCY: "🔴 EMERGENCY",
    }
    return badges.get(urgency, "⚪ UNKNOWN")


def format_summary(assessment: IRAEAssessment) -> str:
    """Generate a brief one-line summary of the assessment."""
    if not assessment.irae_detected:
        return f"{format_urgency_badge(assessment.urgency)} - No irAE signals detected"
    
    systems = assessment.get_affected_system_names()
    systems_str = ", ".join(systems[:3])
    if len(systems) > 3:
        systems_str += f" (+{len(systems) - 3} more)"
    
    return (
        f"{format_urgency_badge(assessment.urgency)} - "
        f"{assessment.causality.likelihood.value} irAE | "
        f"{assessment.overall_severity.value} | "
        f"Systems: {systems_str}"
    )
