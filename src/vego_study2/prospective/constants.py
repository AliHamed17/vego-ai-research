"""Frozen constants for the prospective ON/OFF study.

Every value here is mirrored in the frozen experiment manifest.  The manifest
is authoritative; the manifest loader fails closed if the two disagree.
"""

from __future__ import annotations

STUDY_ID = "VEGO-AI-STUDY-2-PROSPECTIVE"
MANIFEST_SCHEMA = "study2-prospective-manifest-v1"
RECEIPT_SCHEMA = "study2-prospective-receipt-v1"
CASE_SELECTION_SCHEMA = "study2-prospective-case-selection-v1"
BUDGET_SCHEMA = "study2-prospective-budget-reservation-v1"
LEDGER_SCHEMA = "study2-prospective-call-ledger-v1"
AGGREGATE_SCHEMA = "study2-prospective-public-aggregate-v1"
CONDITION_OUTPUT_SCHEMA = "study2-condition-output-v1"

SETTING_ID = "cd_airtravel"
CORPUS_ID = "text2uml_airtravel_253b26dc"
CORPUS_COMMIT = "253b26dc704d523209a5cba79686f8f7fab57d63"
FULL_FRAME_CONTRACT_SCHEMA = "airtravel-full-frame-contract-v1"
LANGUAGE_NAME = "UML"

PROVIDER = "openai"
MODEL = "gpt-5.6-luna"
API_MODE = "chat.completions"
ALLOWED_HOSTS = frozenset({"api.openai.com"})
CREDENTIAL_ENV = "OPENAI_API_KEY"

PRICE_IN_PER_M = 0.20
PRICE_OUT_PER_M = 1.20
RESERVE_INPUT_TOKENS = 12_000
MAX_OUTPUT_TOKENS = 16_384

HARD_CEILING_USD = 6.00
GUARD_CEILING_USD = 5.90
REQUEST_TIMEOUT_SECONDS = 180
OFF_RUN_TIMEOUT_SECONDS = 1_800
ON_RUN_TIMEOUT_SECONDS = 5_400
MAX_CONCURRENT_CASES = 2
TRANSPORT_RETRIES_PER_REQUEST = 1

ON_REQUEST_CAP_PER_CASE = 19
OFF_REQUEST_CAP_PER_CASE = 3
MIN_PAIRED_CASES = 4
SELECTION_SEED = 20260908

CONDITION_ON = "VEGO_AI_ON"
CONDITION_OFF = "VEGO_AI_OFF"
CONDITION_ORDER = (CONDITION_OFF, CONDITION_ON)

OFF_FORBIDDEN_MODULES = (
    "orchestrator",
    "qa_registry",
    "qa_communication",
    "agent1_language_advisor",
    "agent2_domain_advisor",
    "agent3_model_inspector",
    "agent4_variability_explorer",
    "human_review_queue",
    "extract_qa_escalation_features",
    "selective_intervention_policy",
    "study1_signal_contract",
    "airtravel_local_observer",
    "vego_study2.prospective.on_runner",
)

EVIDENCE_PROSPECTIVE = "PROSPECTIVE EMPIRICAL EVIDENCE"
EVIDENCE_FIXTURE = "ENGINEERING-ONLY FIXTURE"
EVIDENCE_NOT_MEASURED = "NOT_MEASURED"
EVIDENCE_NOT_AVAILABLE = "NOT_AVAILABLE"

PRIVATE_ROOT_TOKEN = "${VEGO_PRIVATE_EVIDENCE_ROOT}"
