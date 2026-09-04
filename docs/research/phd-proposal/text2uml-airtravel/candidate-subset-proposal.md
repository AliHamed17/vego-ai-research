# AirTravel candidate-subset proposal

Status: **PROPOSED_NOT_FROZEN**. Claude must freeze the exact selection before any run.

Four independently stored, nonempty, non-stripped outputs are proposed (N=4):

- `result_one_claude-sonnet-4-6.txt` — SHA-256 `240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91`, 1248 bytes; syntax `WRAPPER_PRESENT`
- `result_one_codestral-2508.txt` — SHA-256 `08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6`, 1272 bytes; syntax `WRAPPER_PRESENT`
- `result_one_deepseek-chat.txt` — SHA-256 `ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a`, 1324 bytes; syntax `WRAPPER_PRESENT`
- `result_one_gemini-2.5-flash.txt` — SHA-256 `1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a`, 1231 bytes; syntax `WRAPPER_PRESENT`

Selection uses filename/documented output provenance only. It does not use VEGO-AI outputs, Q&A frequency, Detector-v1, or reference agreement. No candidate is treated as a student or human submission.
