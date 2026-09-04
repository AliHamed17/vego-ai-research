# AirTravel reference-separation receipt

Proposed ignored local layout:

```text
external_data/text2uml/<upstream-commit>/prepared/AirTravel/
  runtime_input/domain_description/description.md
  runtime_input/candidate_models/<candidate files>
  reference_only/plantuml.txt
  reference_only/plantuml_adjusted.txt
  reference_only/extramaterial/<files>
  source_metadata/LICENSE
```

The runtime input contains the domain description and proposed generated candidates only. Reference models and extramaterial are excluded from the VEGO-AI configuration and are never passed to the orchestrator. Candidate bytes are copied without transformation; original and staged hashes are checked by the preparation script.
