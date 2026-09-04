# AirTravel offline compatibility report

- Domain description: UTF-8 decodes successfully.
- Candidate PlantUML: proposed files are nonempty and wrapper-valid; no source bytes were rewritten.
- Filename-to-case mapping: staged copies receive deterministic numeric prefixes (01..N) because the protected loader derives case_id from the prefix; source bytes remain unchanged and duplicate case IDs are avoided.
- Reference exclusion: reference models remain outside runtime_input.
- Configuration paths: repository-relative paths resolve from the config file directory to the ignored prepared pack; no absolute path is embedded.
- Case count N: `4` (proposal only; not frozen).
- Provider/model execution: **not performed**.
- Parser/render check: metadata and wrapper checks only; no scientific result or alert was generated.
