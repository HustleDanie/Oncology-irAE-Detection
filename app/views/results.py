"""Results page for displaying irAE assessment findings."""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.assessment import Urgency, Severity
from src.utils.formatting import format_assessment_output


def render():
    """Render the results page."""
    st.markdown("## 📊 Assessment Results")
    
    # Check if we have results
    if "assessment_result" not in st.session_state or st.session_state.assessment_result is None:
        st.warning("⚠️ No assessment results available. Please run a new assessment first.")
        if st.button("📋 Go to Assessment", type="primary"):
            st.switch_page("pages/assessment.py")
        return
    
    result = st.session_state.assessment_result
    
    # Urgency banner at top
    render_urgency_banner(result)
    
    st.markdown("---")
    
    # Main results in tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Summary", 
        "🏥 Organ Systems", 
        "📋 Recommendations",
        "📄 Full Report"
    ])
    
    with tab1:
        render_summary_tab(result)
    
    with tab2:
        render_organ_systems_tab(result)
    
    with tab3:
        render_recommendations_tab(result)
    
    with tab4:
        render_full_report_tab(result)
    
    # Disclaimer
    st.markdown("---")
    st.markdown("""
    <div class="disclaimer-box">
    <strong>⚠️ Clinical Decision Support Disclaimer</strong><br><br>
    This assessment is for clinical decision support only. It does not replace clinical judgment. 
    All findings should be verified by a qualified clinician before taking clinical action.
    </div>
    """, unsafe_allow_html=True)


def render_urgency_banner(result):
    """Render the urgency banner."""
    urgency_configs = {
        Urgency.EMERGENCY: {
            "class": "urgency-emergency",
            "icon": "🔴",
            "message": "EMERGENCY - Immediate evaluation required"
        },
        Urgency.URGENT: {
            "class": "urgency-urgent", 
            "icon": "🟠",
            "message": "URGENT - Same-day evaluation recommended"
        },
        Urgency.SOON: {
            "class": "urgency-soon",
            "icon": "🟡", 
            "message": "SOON - Oncology review within 1-3 days"
        },
        Urgency.ROUTINE: {
            "class": "urgency-routine",
            "icon": "🟢",
            "message": "ROUTINE - Continue standard monitoring"
        },
    }
    
    config = urgency_configs.get(result.urgency, urgency_configs[Urgency.ROUTINE])
    
    st.markdown(f"""
    <div class="{config['class']}">
    <h3>{config['icon']} {config['message']}</h3>
    <p>{result.urgency_reasoning}</p>
    </div>
    """, unsafe_allow_html=True)


def render_summary_tab(result):
    """Render the summary tab."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🧬 Immunotherapy Context")
        ctx = result.immunotherapy_context
        
        if ctx.on_immunotherapy:
            st.success("✅ Patient is on immunotherapy")
            st.markdown(f"**Agents:** {', '.join(ctx.agents) if ctx.agents else 'Not specified'}")
            st.markdown(f"**Drug Classes:** {', '.join(ctx.drug_classes) if ctx.drug_classes else 'Not specified'}")
            if ctx.combination_therapy:
                st.warning("⚠️ Combination immunotherapy (higher irAE risk)")
        else:
            st.info("ℹ️ No active immunotherapy detected")
        
        st.markdown("---")
        
        st.markdown("### 🎯 irAE Detection")
        if result.irae_detected:
            st.error("⚠️ Possible irAE signals detected")
        else:
            st.success("✅ No clear irAE signals detected")
    
    with col2:
        st.markdown("### 📊 Causality Assessment")
        st.markdown(f"**Likelihood:** {result.causality.likelihood.value}")
        st.markdown(f"**Reasoning:** {result.causality.reasoning}")
        
        if result.causality.temporal_relationship:
            st.markdown(f"**Timing:** {result.causality.temporal_relationship}")
        
        if result.causality.alternative_causes:
            with st.expander("Alternative causes considered"):
                for cause in result.causality.alternative_causes:
                    st.markdown(f"- {cause}")
        
        st.markdown("---")
        
        st.markdown("### 📈 Severity")
        severity_colors = {
            Severity.GRADE_1: "green",
            Severity.GRADE_2: "orange",
            Severity.GRADE_3: "red",
            Severity.GRADE_4: "darkred",
            Severity.UNKNOWN: "gray",
        }
        color = severity_colors.get(result.overall_severity, "gray")
        st.markdown(f"**{result.overall_severity.value}**")
        st.markdown(f"_{result.severity_reasoning}_")
    
    # Key evidence
    st.markdown("---")
    st.markdown("### 🔑 Key Supporting Evidence")
    if result.key_evidence:
        for i, evidence in enumerate(result.key_evidence, 1):
            st.markdown(f"{i}. {evidence}")
    else:
        st.info("No specific evidence points highlighted")
    
    # Confidence Score
    if result.confidence_score:
        st.markdown("---")
        st.markdown("### 📊 Assessment Confidence")
        
        conf = result.confidence_score
        
        # Overall confidence with color coding
        confidence_colors = {
            "High": "green",
            "Moderate": "orange",
            "Low": "red",
            "Very Low": "darkred",
        }
        level = conf.confidence_level
        color = confidence_colors.get(level, "gray")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Overall Confidence",
                value=f"{conf.overall_confidence:.0%}",
                delta=level
            )
        
        with col2:
            st.metric(
                label="Evidence Strength",
                value=f"{conf.evidence_strength:.0%}"
            )
        
        with col3:
            st.metric(
                label="Data Completeness",
                value=f"{conf.data_completeness:.0%}"
            )
        
        # Show details in expander
        with st.expander("View confidence details"):
            if conf.confidence_factors:
                st.markdown("**✅ Factors supporting confidence:**")
                for factor in conf.confidence_factors:
                    st.markdown(f"- {factor}")
            
            if conf.uncertainty_factors:
                st.markdown("**⚠️ Factors reducing confidence:**")
                for factor in conf.uncertainty_factors:
                    st.markdown(f"- {factor}")
            
            st.markdown(f"**Rule matches:** {conf.rule_match_count} organ-specific patterns detected")


def render_organ_systems_tab(result):
    """Render the organ systems tab."""
    st.markdown("### 🏥 Organ System Analysis")
    
    # Separate affected and unaffected systems
    affected = [f for f in result.affected_systems if f.detected]
    unaffected = [f for f in result.affected_systems if not f.detected]
    
    if affected:
        st.markdown("#### ⚠️ Systems with Detected Signals")
        
        for finding in affected:
            with st.expander(f"🔴 {finding.system.value} - {finding.severity.value if finding.severity else 'Severity unknown'}"):
                st.markdown("**Findings:**")
                for f in finding.findings:
                    st.markdown(f"- {f}")
                
                st.markdown("**Evidence:**")
                for e in finding.evidence:
                    st.markdown(f"- {e}")
                
                if finding.confidence:
                    st.progress(finding.confidence, text=f"Confidence: {finding.confidence:.0%}")
    else:
        st.success("✅ No organ system signals detected")
    
    if unaffected:
        st.markdown("#### ✅ Systems Without Detected Signals")
        unaffected_names = [f.system.value for f in unaffected]
        st.markdown(", ".join(unaffected_names))


def render_recommendations_tab(result):
    """Render the recommendations tab."""
    st.markdown("### 📋 Recommended Actions")
    
    if result.recommended_actions:
        for action in sorted(result.recommended_actions, key=lambda x: x.priority):
            priority_emoji = "🔴" if action.priority == 1 else "🟡" if action.priority == 2 else "🟢"
            
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 1rem; margin: 0.5rem 0; border-radius: 5px;">
            <strong>{priority_emoji} Priority {action.priority}:</strong> {action.action}<br>
            <em style="color: #666;">{action.rationale if action.rationale else ''}</em>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No specific actions recommended. Continue routine monitoring.")
    
    # General guidance
    st.markdown("---")
    st.markdown("### 📚 General irAE Management Principles")
    with st.expander("View general guidance"):
        st.markdown("""
        **Key principles for irAE management:**
        
        1. **Early recognition is critical** - irAEs can progress rapidly
        2. **Hold immunotherapy** for Grade 2+ toxicities (with oncology guidance)
        3. **Corticosteroids** are the mainstay of treatment for most irAEs
        4. **Specialty consultation** may be needed (GI, pulmonology, endocrine, etc.)
        5. **Document thoroughly** and communicate with the oncology team
        
        **When to escalate:**
        - Grade 3-4 toxicity
        - Rapidly progressing symptoms
        - Multi-organ involvement
        - Failure to respond to initial management
        """)


def render_full_report_tab(result):
    """Render the full text report."""
    st.markdown("### 📄 Full Assessment Report")
    
    # Generate formatted report
    report = format_assessment_output(result)
    
    # Display in code block for easy copying
    st.code(report, language=None)
    
    # Download button
    st.download_button(
        label="📥 Download Report",
        data=report,
        file_name=f"irae_assessment_{result.assessment_date.strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
    )
