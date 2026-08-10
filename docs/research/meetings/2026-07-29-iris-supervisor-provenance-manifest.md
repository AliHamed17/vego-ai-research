# Provenance Manifest — 29 July 2026 Iris Supervisor Call

> **Status:** Complete local machine-transcription package; human bilingual review and full diarization pending.

- Integrity refresh: `2026-08-10T18:11:46.365923+03:00`
- Repository base revision at refresh: `0595590216b9ec832de6f70b11f0da8b87e85c6b` (the Aug-10 gate-repair commit following the 2026-08-05 meeting-record merge; all frozen package paths below are byte-identical to this commit)
- Working-tree note: the working tree matches this revision for every frozen package path; it is not the human RG-04 release freeze. The local PDF and workbooks remain intentionally ignored and are bound below by exact hashes; the older backup ZIP is explicitly stale. Any post-rehearsal package correction requires a new artifact hash and base revision. A provenance-only descendant may record this binding without changing the controlled package paths.

The integrity refresh revalidated the immutable raw media, ASR, and machine-translation hashes without changing those files. Derived call and governance artifacts received new hashes after their controlled documentation updates.

## Source inventory and integrity

| Role | Local path | Bytes | Last modified | SHA-256 | Intended use |
| --- | --- | --- | --- | --- | --- |
| Metadata | C:\Users\ahamed\OneDrive - Parallel Wireless\Documents\Zoom\2026-07-29 09.03.44 Iris Reinhartz-Berger's Personal Meeting Room\recording.conf | 127 | 2026-07-29T09:58:46.394914+03:00 | 34EAFDDF04B95D996BD59C239C6C6F916F4E5E0479F067FB8F23045B55EEB8A0 | Zoom pairing/process metadata |
| Primary audio | C:\Users\ahamed\OneDrive - Parallel Wireless\Documents\Zoom\2026-07-29 09.03.44 Iris Reinhartz-Berger's Personal Meeting Room\audio1589041291.m4a | 31536858 | 2026-07-29T09:58:45.438393+03:00 | D4F98015CCBB7BAEBD76B8A7259D3A9FD57C0BAA6579EB538C19EA0FFE6B7D84 | ASR source |
| Primary video | C:\Users\ahamed\OneDrive - Parallel Wireless\Documents\Zoom\2026-07-29 09.03.44 Iris Reinhartz-Berger's Personal Meeting Room\video1589041291.mp4 | 288382283 | 2026-07-29T09:58:45.395192+03:00 | 11692B3777914CB4BCF8DC0CFAE909878E762149AE3CA2F031A16C4EC6473A77 | Visual participant/speaker review |
| Hebrew ASR JSONL | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-asr.he.jsonl | 279463 | 2026-08-04T00:46:43.420443+03:00 | 952918CA15A36AC08E481C503D469E01BC00AA1A7554C97EF1D552EA2E2EC29B | Preserved timestamped machine source |
| Hebrew SRT | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-asr.he.srt | 92982 | 2026-08-04T00:46:43.422602+03:00 | F68AF8E705D17AD33E54B7C7587592D6BC1569A0F1A2D24ECB9C336F464DD5AC | Subtitle draft |
| Hebrew text | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-asr.he.txt | 82214 | 2026-08-04T00:46:43.423606+03:00 | 40EBD629FB1A851718F3A07C5E145757A9FB51ABC67012DD95519642EF8DE6A1 | Readable ASR draft |
| ASR metadata | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-asr.he.metadata.json | 519 | 2026-08-04T00:46:43.421443+03:00 | FE4F41E80621221176221C5999F152F5A34C9A4DCF1D3415CBFC407E5BDA64B2 | Engine/model settings |
| Bilingual machine JSONL | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-asr.he-en.machine.jsonl | 355737 | 2026-08-04T00:46:43.419442+03:00 | 9BF59566AF1177CDC633EB58DF7A193EC4E4889A8BBE9ACD8BBBDB661534BA59 | Aligned local English translation |
| Bilingual transcript | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-bilingual-transcript.he-en.md | 424648 | 2026-08-04T00:46:43.425172+03:00 | A0222A18A839970506A5B9AC656E5B6DDF57F3A7417CDCE416AF4050D34836EE | Reader-facing segment record |
| Preliminary Zoom disposition CSV | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-zoom-preliminary-disposition.csv | 389121 | 2026-08-04T00:46:43.430197+03:00 | 16E39F4257C5B0E645A1EB6DAAC30046B83DA635CD22054CA67496DAF1F5C90C | Machine-only 1,195-row human-review input; not adjudicated evidence |
| Preliminary Zoom disposition JSON | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-zoom-preliminary-disposition.json | 991367 | 2026-08-04T00:46:43.432198+03:00 | E0E312A339C37E61F2A1C4E8C73E79CA558134E2482819F737F75A6FFDFCD7D0 | Machine-only 1,195-row human-review input; not adjudicated evidence |
| Machine gap ledger | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-zoom-machine-gap-ledger.csv | 144920 | 2026-08-04T00:46:43.428198+03:00 | 169C3A5203930936C40BAECCD8AF5DB0E097B7942C821605201FE64DC0AF3D1D | Deterministic 934-row lead/internal/tail uncovered-interval accounting; machine-only, human classification pending |
| Call report | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-call-report.md | 12891 | 2026-08-04T00:46:43.425172+03:00 | E740954D52094AA04C7F286B97E6604572298B4988418236C849048F424342D1 | Analytical summary with complete chronological coverage, cautious attribution, and priority human-review ranges |
| Requirements snapshot | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-requirements-register.md | 16406 | 2026-08-04T00:46:43.417444+03:00 | 49C92138B264FF549E75C6957A1706FC1A7119F680116814DC31DD5F1E922F18 | Immutable call-time requirements extraction snapshot |
| Actions/questions snapshot | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-supervisor-action-register.md | 12382 | 2026-08-04T00:46:43.417444+03:00 | 93635CF9765A8BFC27A772D622B152389F8CDDD0FBA5318616166C02B8087C2E | Immutable call-time action/open-question extraction snapshot |
| Closure governance control | C:\Users\ahamed\vego-ai\docs\research\phd-proposal\iris-closure-governance-control.md | 7494 | 2026-08-04T00:46:43.449316+03:00 | 65D72408EB575F0E844479C50D5CB4E475EDD5D17431604DD51B4357B9DF0725 | Authoritative-record order, status dimensions, human-review workflow, and closure rules |
| External-fact register | C:\Users\ahamed\vego-ai\docs\research\phd-proposal\external-fact-register.md | 7147 | 2026-08-04T00:46:43.447316+03:00 | 498D8410F68A0B035D7BC65C61788EEA33819E6ECE46DF0334C063FB7E3D48B3 | Meeting-statement claims and independent-verification states |
| Closure certificate template | C:\Users\ahamed\vego-ai\docs\research\phd-proposal\iris-closure-certificate-template.md | 8913 | 2026-08-04T00:46:43.448316+03:00 | BBCA840D859EAD74C1310E0713666668DE069B740542E612CA5F912277D192AF | Versioned unissued certificate form with executable validator commands and receipt-binding fields |
| Master traceability register | C:\Users\ahamed\vego-ai\docs\research\phd-proposal\master-traceability-register.md | 40758 | 2026-08-10T18:09:56.661654+03:00 | 3FCF5AC92249DEE62789386AA80DF4E5EAA4D9E3220B4D0014A0F5AB21663CD1 | Canonical current control status with independent extraction, implementation, acceptance, and ongoing-control dimensions |
| Closure audit | C:\Users\ahamed\vego-ai\docs\research\phd-proposal\iris-requirements-closure-audit.md | 25178 | 2026-08-04T00:46:43.449316+03:00 | 1A52D7A0D1F292582045FA8DF3129C8E315454C65B38BB2D03CCC398881F073A | Canonical 44-control readiness audit and evidence-bounded release statement; stale-backup boundary explicit |
| Presentation/control manifest | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-08-05-supervisor-presentation-manifest.md | 12706 | 2026-08-04T00:46:43.435991+03:00 | 3CD6779F09BB8F8B95BDCD29B9AA3AE4C103D737F2A6633D4258DD26DAEEC70C | Built-package map for all 44 baseline controls; current corrected deck hashes recorded; human release gates remain open |
| Rehearsal record | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-08-05-supervisor-rehearsal-record.md | 9453 | 2026-08-04T00:46:43.435991+03:00 | 11ED4436E1B843014A868036BE3E5516120E68302AC815E316E95DA19AF07EB4 | Automated/render preflight PASS; native title/footer and machine-alignment wording corrections inspected; human timed and adversarial rehearsals NOT RUN |
| Adversarial Q&A worksheet | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-08-05-supervisor-adversarial-qa-worksheet.md | 5931 | 2026-08-04T00:46:43.433481+03:00 | F7168A86AC627C46BDEED75019E2777E9928324B21674E49B30A13E199EEEF32 | Twelve evidence-bound challenge prompts; human run NOT RUN |
| Delivery/access record | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-08-05-supervisor-delivery-access-record.md | 6299 | 2026-08-04T00:46:43.433481+03:00 | 4422FEBE76846D691C6AB484D1ACD832A2B37262C5D46E70584740247B90037C | Exact corrected local package hashes recorded; stale backup explicitly invalidated; package NOT SHARED and access NOT TESTED |
| Supervisor presentation PPTX | C:\Users\ahamed\vego-ai\presentations\VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pptx | 98468 | 2026-08-04T00:46:43.580287+03:00 | 7765132B6406796AFE802887A9CC69B9A903843BDCBEC606C517738D91421D24 | Corrected 12-slide English core plus nine-slide appendix; 21 source-note sections; native title/footer and machine-alignment wording normalized; local build only |
| Supervisor presentation PDF | C:\Users\ahamed\vego-ai\presentations\VEGO-AI-Iris-Supervisor-Decisions-2026-08-05.pdf | 335921 | 2026-08-03T22:08:00.262506+03:00 | A8E296911F734477ADD5005BF02C305DFCA4C9E897532DA510A3D629E700F7EC | Native PowerPoint export of the corrected 21-slide PPTX; local build only |
| Zoom human-review workbook | C:\Users\ahamed\vego-ai\outputs\iris-closure-2026-08-01\Iris_Zoom_Review_Ledger_2026-07-29.xlsx | 146350 | 2026-08-01T12:41:39.532937+03:00 | 7F72BC625374C225B8C450E6A9EE5F4A6D147988BF35AF3BC54D4F5FC7C3F295 | 1,195-row machine-only review interface; human review/adjudication pending |
| Local offline package backup | C:\Users\ahamed\vego-ai\outputs\iris-closure-2026-08-01\VEGO-AI-August5-Supervisor-Package-local-backup.zip | 477215 | 2026-08-01T13:13:56.518417+03:00 | AAD3065C157A9C2056DAD687E26451A7D6941626AB9E7A77D177831F483420B3 | STALE / INVALIDATED after the PPTX/PDF correction; local and not delivered; rebuild only after rehearsal and RG-04 |
| Human-review workflow | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-zoom-human-review-workflow.md | 1363 | 2026-08-04T00:46:43.427199+03:00 | 5DD55E924B4CF2BD91B5D895A2B31E1994FEE5DFF7A31B914AE7D5BA925883B4 | Separate two-reviewer and third-person adjudication workflow; currently 0/1,195 plus 0/1 full-media record per reviewer |
| Reviewer A return template | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-zoom-reviewer-a.csv | 169 | 2026-08-04T00:46:43.432480+03:00 | 6814C7FEE3C8E7077D6F637FCC342B4E372C5027BA52058CFCE59701C0A2AF15 | Header-only human return; no review evidence present |
| Reviewer B return template | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-zoom-reviewer-b.csv | 169 | 2026-08-04T00:46:43.432480+03:00 | 6814C7FEE3C8E7077D6F637FCC342B4E372C5027BA52058CFCE59701C0A2AF15 | Header-only independent human return; no review evidence present |
| Adjudication return template | C:\Users\ahamed\vego-ai\docs\research\meetings\2026-07-29-iris-zoom-adjudication.csv | 223 | 2026-08-04T00:46:43.426193+03:00 | D35B21E7F2951F07FF2E6FA1AF51B46926C7C89EF52F731454AB45C4018A8BCA | Header-only third-person adjudication return; no decisions present |
| Adjudicated-ledger merger | C:\Users\ahamed\vego-ai\scripts\build_iris_zoom_adjudicated_ledger.py | 19075 | 2026-08-04T00:46:43.629032+03:00 | B98DC07AC6FC0CAB008D2BEB64A1C5C2B05286039527E090CE83C76609E828D0 | Deterministic fail-closed merger; pending mode writes no adjudicated output |
| Authorized receipt schema | C:\Users\ahamed\vego-ai\schemas\iris-authorized-submission-receipt-v1.schema.json | 4637 | 2026-08-04T00:46:43.607978+03:00 | A4AB94CFFA46FF56F24E17C9AB151EC2AF6FB27FDA6522368D21400B389AB7A0 | Submission receipt, package, authorization, and certificate-binding contract |
| Authorized receipt pending template | C:\Users\ahamed\vego-ai\docs\research\phd-proposal\authorized-submission-receipt.template.json | 754 | 2026-08-04T00:46:43.445311+03:00 | 5477BB768263FE0F6680635243CA87897D161E22C2E3CD8AC504947C07795D6A | Explicitly NOT_SUBMITTED; not a receipt or submission claim |

## Transformation chain

1. Zoom M4A/MP4 retained unchanged.
2. Hebrew ASR generated locally with `faster-whisper 1.2.1`, cached `large-v3-turbo`, CPU `int8`, language `he`, beam 5, VAD enabled.
3. ASR produced 1,195 sequentially identified segments from `00:00:01.060` to
   `00:46:25.010`; detected language Hebrew, probability `1.0` under the
   fixed-language run. The timestamps are not temporally contiguous: the ASR
   interval union covers `2,333.500` of `2,786.283` seconds (`83.750%`). A
   deterministic machine ledger enumerates `934` uncovered intervals totaling
   `452.783` seconds: one `1.060`-second lead, `932` internal intervals totaling
   `450.450` seconds, and one `1.273`-second tail. Their meaning remains pending
   full-media human classification.
4. Each Hebrew segment was translated locally through Ollama `qwen2.5:7b`, temperature 0, with immutable segment IDs; no recording/transcript content was uploaded to an external service.
5. Analytical reports were built from the aligned JSONLs. Terminology was corrected in paraphrases without changing raw ASR or raw machine translation.
6. The preliminary disposition CSV/JSON were generated deterministically for all 1,195 segments from the immutable machine record and call-time registers. They retain machine-only review status and are inputs to, not substitutes for, independent bilingual review and adjudication.
7. The workbook projects the same machine record into a reviewer-friendly interface without promoting any row to human-reviewed status.
8. The August 5 PPTX was built from controlled research sources; its two inconsistent appendix-title runs and clipped slide-11 footer were normalized in native PowerPoint, then exported to PDF. The corrected package was tested for overflow and visually inspected through all 21 PowerPoint-native renders, including direct 1600x900 exports of the changed slides. Those local checks do not constitute human rehearsal, Ali release approval, delivery, recipient access, or supervisor acceptance.
9. Human review remains separate from the deterministic preliminary ledger. Two complete independent returns plus a third-person decision for every disagreement are required before the merger can emit adjudicated CSV/JSON; the tracked header-only inputs currently produce a valid pending state and no output.
10. Final submission closure requires one exact verified receipt record conforming to the receipt schema and hash-bound to the submitted package, external receipt artifact, authorization evidence, and issued certificate. The tracked template is explicitly `NOT_SUBMITTED` and cannot satisfy closure.

## Speaker evidence

- The Zoom video is a stable three-person gallery: Iris (upper-left), Ali (upper-right), Arnon (lower tile).
- The mixed AAC track has identical left/right channels and no per-speaker isolation.
- Visual review confirms Iris speaking at the opening; S-0001–S-0006 are high-confidence Iris. Later attribution uses female/male grammar, conversational turns, named-address cues, and is marked medium where used analytically.
- The transcript itself does not assign names beyond S-0001–S-0006.

## Known limitations

- Hebrew and English transcript text is machine-derived and can contain lexical errors or cross-segment drift.
- Important recurring errors include study/stage, data/diet, software engineering/modeling, variability, MIMIC, Claude, LLM, Clalit, and Haifa District. Analytical paraphrases correct these using Hebrew and context.
- Speaker labels are not automatic diarization. A named attribution must retain its confidence statement.
- The ASR/VAD interval union does not cover the complete media timeline. Its
  machine gap ledger is an accounting interface, not evidence that uncovered
  intervals are silence or non-substantive.
- Statements about university policy, hospitals, datasets, data volumes, access, privacy, or deadlines are meeting statements unless independently verified elsewhere.
- The English transcript is not suitable for direct quotation until bilingual review.

## Correction policy

Never change the raw media or raw JSONL in place. Record future corrections as reviewed fields or a separate correction log with segment ID, original text, corrected text, reviewer, date, and reason. Recompute hashes after any derived-artifact update.
