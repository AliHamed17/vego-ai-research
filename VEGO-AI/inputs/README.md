# Inputs

Fixed research inputs and reference data for the VEGO-AI pipeline.

## Language bases

- \language_base_ucd.txt\ — UML Use Case Diagram language constructs and definitions
- \language_base_cd.txt\ — UML Class Diagram language constructs and definitions

## Domain bases

### ParkWise (parking management system)

- \pw/domain_description.txt\ — domain overview and context
- \pw/domain_base_ucd.txt\ — ParkWise-specific Use Case Diagram guidelines
- \pw/domain_base_cd.txt\ — ParkWise-specific Class Diagram guidelines

### Cheers (beer distribution system)

- \ch/domain_description.txt\ — domain overview and context
- \ch/domain_base_ucd.txt\ — Cheers-specific Use Case Diagram guidelines
- \ch/domain_base_cd.txt\ — Cheers-specific Class Diagram guidelines

## Evaluation schema

- \scoring_schema.txt\ — how student models are scored against guidelines

## Examples

- \human_feedback.example.jsonl\ — example human feedback records for M1-M4 milestones

## Usage

These inputs are fixed for a given research cycle. They are read by:
- \ramework/orchestrator.py\ — loads inputs for Agents 1–4
- \val/evaluator.py\ — loads inputs for evaluation phases A–C
