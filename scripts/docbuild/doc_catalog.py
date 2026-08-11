#!/usr/bin/env python3
"""Catalogue of every working-Drive document: source, folder, title, status line.

Status lines are written to state each document's honest current condition, so a
reader who opens one file in isolation is not misled about approval or evidence.
"""

# (repo-relative source, drive folder, published base name, document title, status line)
CATALOG = [
    # ---------------- 00_Admin_and_Decisions ----------------
    ("docs/research/phd-proposal/master-traceability-register.md", "00_Admin_and_Decisions",
     "Master Traceability Register (44 controls)", "Master Traceability Register",
     "Internal working baseline - supervisor confirmation and bilingual review remain pending. Requirement acceptance is 0 of 19."),
    ("docs/research/phd-proposal/decision-change-log.md", "00_Admin_and_Decisions",
     "Decision and Change Log", "Decision and Change Log",
     "Working record of controlled changes. A logged entry is not supervisor approval."),
    ("docs/research/phd-proposal/resource-raci-raid-register.md", "00_Admin_and_Decisions",
     "RACI and RAID Register", "Resource RACI and RAID Register",
     "Working document. Several accountable roles remain unfilled; unfilled roles are shown as such, not inferred."),
    ("docs/research/phd-proposal/university-process-verification-checklist.md", "00_Admin_and_Decisions",
     "University Process Verification Checklist", "University Process Verification Checklist",
     "Open - no authoritative university response has been received. Every field remains pending."),
    ("docs/research/phd-proposal/university-process-inquiry-draft.md", "00_Admin_and_Decisions",
     "University Process Inquiry (DRAFT - NOT SENT)", "University Candidacy Process Inquiry",
     "DRAFT - NOT SENT. No recipient, authorization, delivery, or response is recorded."),
    ("docs/research/phd-proposal/external-fact-register.md", "00_Admin_and_Decisions",
     "External Fact Register", "External-Fact Register",
     "Seeded from meeting statements only; most claims remain unverified by an authoritative source."),
    ("docs/research/phd-proposal/claim-register.md", "00_Admin_and_Decisions",
     "Claim Register", "Claim Register",
     "Controls the wording of every claim. No claim in this programme is stated above its evidence state."),
    ("docs/research/phd-proposal/iris-closure-governance-control.md", "00_Admin_and_Decisions",
     "Closure Governance Control", "Closure Governance Control",
     "Defines the authoritative-record order and closure rules. A passing automated check does not close a human gate."),

    # ---------------- 01_Research_Questions ----------------
    ("docs/research/phd-proposal/three-study-contract.md", "01_Research_Questions",
     "Three-Study Contract", "Three-Study Contract",
     "Working contract. Research-question wording is provisional pending D-RQ-01 and D-RQ-02 sign-off."),
    ("docs/research/phd-proposal/2026-08-05-rq-decision-pack.md", "01_Research_Questions",
     "Research Question Decision Pack (2026-08-05)", "Research-Question Decision Pack",
     "Prepared for supervisor decision. Outcomes are not yet logged; wording remains provisional."),
    ("docs/research/phd-proposal/legacy-rq-crosswalk.md", "01_Research_Questions",
     "Legacy Research Question Crosswalk", "Legacy Research-Question Crosswalk",
     "Traceability from the retired multi-question set to the current one-plus-three architecture."),
    ("docs/research/phd-proposal/artifact-per-rq-brainstorm-2026-08-10.md", "01_Research_Questions",
     "Artifact per Research Question (thinking notes only)", "Artifact per Research Question",
     "Informal brainstorm only - not a decision and not a design. Formal artifact design is deliberately deferred."),

    # ---------------- 02_PhD_Proposal ----------------
    ("docs/research/phd-proposal/proposal-v0.1.md", "02_PhD_Proposal",
     "Proposal v0.1", "PhD Proposal, version 0.1",
     "Working draft. Not submitted, not approved; no accuracy, generalization, or clinical claim is made."),
    ("docs/research/phd-proposal/proposal-v0.2-working-draft.md", "02_PhD_Proposal",
     "Proposal v0.2 (working delta)", "PhD Proposal, version 0.2 working delta",
     "A controlled delta over v0.1, not a self-contained proposal. Its own release criteria are not yet met."),
    ("docs/research/phd-proposal/2026-07-29-doctoral-execution-plan.md", "02_PhD_Proposal",
     "Doctoral Execution Plan (2026-07-29)", "Doctoral Execution Plan",
     "Working plan. Dates are internal working targets, not confirmed university deadlines."),

    # ---------------- 03_Literature_Review ----------------
    ("literature/per-rq-literature-map.md", "03_Literature_Review",
     "Per-RQ Coverage Gap Map", "Per-Research-Question Literature Coverage Map",
     "Inventory and gap analysis only. No database search has been executed, so no novelty or completeness claim is supported."),
    ("docs/research/phd-proposal/literature-review-protocol.md", "03_Literature_Review",
     "Literature Review Protocol", "Literature Review Protocol",
     "Protocol document. Defines how the review will be run; it is not evidence that any search was run."),
    ("docs/research/phd-proposal/literature-search-execution-register.md", "03_Literature_Review",
     "Search Execution Register (QL-01 to QL-05, NOT RUN)", "Literature Search Execution Register",
     "PROTOCOL READY / NOT RUN. Every query row is deliberately unexecuted; an unrun query establishes nothing."),
    ("docs/research/literature-review-taxonomy.md", "03_Literature_Review",
     "Literature Review Taxonomy", "Literature Review Taxonomy",
     "Working taxonomy for classifying sources. Subject to revision at D-RQ-08."),

    # ---------------- 04_SE_Modeling_Studies ----------------
    ("docs/research/baseline-characterization.md", "04_SE_Modeling_Studies",
     "Baseline Characterization", "Baseline Characterization",
     "Descriptive characterization of the software/modeling corpus. Not a performance result."),
    ("docs/research/evaluation-report.md", "04_SE_Modeling_Studies",
     "Evaluation Report", "Evaluation Report",
     "Mechanism and architecture readiness only. EXP-005 stands at 0 supplied expert labels; no accuracy or generalization figure is computable."),
    ("docs/research/expert-labeling-protocol.md", "04_SE_Modeling_Studies",
     "Expert Labeling Protocol (EXP-005)", "Expert Labeling Protocol",
     "Defines how independent expert labels must be produced. 0 of 24 generalization-safe rows are labelled; the gate needs at least 20."),
    ("docs/research/bigui/EXPERIMENT_BENCHMARK_ANALYTICS_REPORT.md", "04_SE_Modeling_Studies",
     "Experiment Benchmark Analytics Report", "Experiment Benchmark Analytics Report",
     "Engineering benchmark material. Latency and overhead figures are machine measurements, not research results."),
    ("docs/research/phd-proposal/iris-alignment-experiment-register.md", "04_SE_Modeling_Studies",
     "IRIS-EXP Alignment Experiment Register", "IRIS-EXP Alignment Experiment Register",
     "Structure checks pass; readiness and closure gates remain open pending human evidence."),
    ("docs/research/phd-proposal/scientific-experiment-crosswalk.md", "04_SE_Modeling_Studies",
     "Scientific Experiment Crosswalk", "Scientific Experiment Crosswalk",
     "Maps experiments to research questions and claim states. Planned experiments are marked as planned."),

    # ---------------- 05_Medical_Feasibility_Gated ----------------
    ("docs/research/governance/medical-readiness-scorecard.md", "05_Medical_Feasibility_Gated",
     "Medical Readiness Scorecard (0 of 6 gates)", "Medical Track Readiness Scorecard",
     "NO-GO - BLOCKED. 0 of 6 mandatory entry gates passed. No row-level work, pilot, export, or medical claim is authorized."),
    ("docs/research/governance/medivaria-medical-extension-overview.md", "05_Medical_Feasibility_Gated",
     "MediVARIA - Medical Extension Overview", "MediVARIA - Medical Extension Overview",
     "Derived summary of a supplied one-page proposal. Not a decision, not a design, not verified evidence."),
    ("docs/research/governance/mimic-metadata-audit-2026-07-30.md", "05_Medical_Feasibility_Gated",
     "MIMIC Metadata-Only Audit (2026-07-30)", "MIMIC Metadata and Schema Audit",
     "Metadata and schema only - no patient row was inspected. MIMIC is not selected and no elapsed-time claim is made."),
    ("docs/research/governance/clalit-research-request-template.md", "05_Medical_Feasibility_Gated",
     "Clalit Research Request Template", "Clalit Research Request Template",
     "Blank template. No request has been submitted and no partner access exists."),
    ("docs/research/governance/phd-data-boundary.md", "05_Medical_Feasibility_Gated",
     "PhD Data Boundary (three zones)", "PhD Data Boundary",
     "Binding zone rules. Patient rows and restricted derivatives never enter the repository, ordinary Drive, or online models."),
    ("docs/research/governance/medical-derived-artifact-provenance-template.md", "05_Medical_Feasibility_Gated",
     "Medical Derived-Artifact Provenance Template", "Medical Derived-Artifact Provenance Template",
     "Blank template for a future authorized artifact. No medical artifact has been produced or approved for export."),

    # ---------------- 06_Weekly_Meetings ----------------
    ("docs/research/meetings/2026-08-05-supervisor-meeting.md", "06_Weekly_Meetings",
     "2026-08-05 Meeting Record (machine transcript, unreviewed)", "Supervisor Meeting Record, 5 August 2026",
     "Machine-derived record with inferred (undiarized) speakers. Not human-reviewed; not quotable as verbatim."),
    ("docs/research/meetings/2026-08-05-execution-plan.md", "06_Weekly_Meetings",
     "2026-08-05 Execution Plan", "Execution Plan following the 5 August call",
     "Working plan derived from the machine record. Not supervisor-approved."),
    ("docs/research/meetings/2026-08-05-tracking.md", "06_Weekly_Meetings",
     "2026-08-05 Step Tracking", "Step Tracking following the 5 August call",
     "Live status of the eight steps agreed after the call. Statuses reflect evidence, not intent."),
    ("docs/research/meetings/2026-07-29-iris-supervisor-call-report.md", "06_Weekly_Meetings",
     "2026-07-29 Call Report", "Supervisor Call Report, 29 July 2026",
     "Analytical summary of a machine-derived transcript. Attribution is cautious and human review remains pending."),
    ("docs/research/meetings/2026-07-29-iris-requirements-register.md", "06_Weekly_Meetings",
     "2026-07-29 Requirements Register", "Requirements Register, 29 July 2026",
     "Immutable call-time extraction snapshot. Superseded status lives in the master traceability register."),
    ("docs/research/meetings/2026-07-29-iris-supervisor-action-register.md", "06_Weekly_Meetings",
     "2026-07-29 Action Register", "Action and Open-Question Register, 29 July 2026",
     "Immutable call-time extraction snapshot. Current status lives in the master traceability register."),
    ("docs/templates/weekly-supervisor-pre-read.md", "06_Weekly_Meetings",
     "TEMPLATE - Weekly Supervisor Pre-Read", "Weekly Supervisor Pre-Read (template)",
     "Blank template for each weekly cycle. No complete weekly cycle has yet been recorded."),
]

if __name__ == "__main__":
    from collections import Counter
    c = Counter(row[1] for row in CATALOG)
    for k in sorted(c):
        print(f"{k:32} {c[k]}")
    print(f"{'TOTAL':32} {len(CATALOG)}")
