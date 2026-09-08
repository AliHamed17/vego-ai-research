# VEGO-AI Study 2 status dashboard

| Field | Current value |
|---|---|
| Study | `VEGO-AI-STUDY-2` |
| Intervention | `SYSTEM_COMPARISON` |
| Setting | `cd_airtravel` |
| Corpus | `text2uml_airtravel_253b26dc` |
| Cases | 4 frozen identifiers (`01`–`04`) |
| ON condition | Multi-agent + inter-agent Q&A |
| OFF condition | Direct per-case workflow; no Q&A |
| Detector-v1 OFF denominator | `NOT_APPLICABLE` |
| Engineering fixture | Prepared; local-only and deterministic |
| Scientific run | **NOT_EXECUTED** |
| Scientific result | **NONE** |
| Human scores | **NONE** |
| Provider/API calls | **0 in this phase** |
| Study 1 pooling | `false` |

## Interpretation boundary

This dashboard records readiness and controls only. It must not be read as an
ON/OFF performance comparison. The deterministic fixture can establish that
the instrument rejects malformed outputs, records hashes and separates the
conditions; it cannot establish accuracy, quality, usefulness, human benefit,
generalization, or superiority.

## Next gates

Independent preregistration review, immutable-head green CI, provider/model and
budget freeze, fresh one-time authorization, and a later blinded human
evaluation are required before scientific reporting.
