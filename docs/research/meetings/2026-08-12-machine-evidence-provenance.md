# August 12 machine-evidence provenance status

Status: **machine-derived Hebrew and English; human verification incomplete**.

This sanitized record contains no transcript text, private filesystem path, raw media, or
speaker attribution. It records the evidence boundary and the hashes needed to identify the
private source chain. A successful structural check is not bilingual review, supervisor
acceptance, delivery, or closure.

## Locked source chain

| Logical role | Bytes | SHA-256 |
| --- | ---: | --- |
| `ZOOM_AUDIO_M4A` | 35,684,965 | `E562AE340AB8FF87BEB84AA03D5BFD709A01A396F0045F2CAE4EEE71C4C0E798` |
| `ZOOM_VIDEO_MP4` | 226,239,003 | `617824ABBA9A9A1626BB73BDEC536ADC6C3A0F3F2A27CFE0335ECE3FC93E435C` |
| `ZOOM_CHAT_TXT` | 315 | `4682711493FD4CA6F694DB0EE0FC116497A8D0A9DA28EB1744F3D070E8E00F94` |
| `ZOOM_RECORDING_CONF` | 127 | `124659343355D5A0EC76C053EC3958BDA39F51BCC7095A19A22A65C902574C7F` |
| `MACHINE_HE_JSONL` | 93,920 | `A9267A95B0F93715375D3A21C2E4C897D7E0682EC0552811E4478831C994EC4D` |
| `MACHINE_HE_READABLE` | 70,581 | `3CC7E56757B83BE416089247D4C8053D56A7F03C1A47699163670F421976EE32` |
| `MACHINE_EN_ATTEMPT_02` | 168,996 | `E163DC80783C2AECE0467FAA2456D0536BA950001D917A6C25B4D3013C8DC25B` |

The M4A and MP4 each decode to 51,591,168 canonical 16 kHz mono samples, or
3,224.448 seconds. Their encoded packets, packet timing, and decoded PCM match. Canonical PCM
SHA-256 is `60D4A3A25CBBEC7ADC68486E5397355D903C028B55A27A9488E5F77898723266`.
The media timeline contains 1,064 ASR segments and 215 uncovered intervals totaling
166.788 seconds; the human reviewers must inspect both the segments and every interval.

## Model and execution bindings

- Hebrew ASR is bound to the recovered generator and task output, the
  `mobiuslabsgmbh/faster-whisper-large-v3-turbo` snapshot at commit
  `0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf`, snapshot-tree SHA-256
  `4EDA58772FE73D11E2ECF35D63D1F22F8296181CE6BFEA849B612C3FD574C74D`, and
  model-blob SHA-256
  `E76620F83D5F5B69EFD3D87E3DC180C1BD21DF9FBEBACFD4335E5E1EFCC018DA`.
- Machine English attempt 02 is bound to local `qwen2.5:7b`, model digest
  `845DBDA0EA48ED749CAAFD9E6037047AA19ACFCFD82E704D7CA97D631A0B697E`,
  frozen options, source hashes, generator hash, prompt-template hash, checkpoints, and one
  same-run completion record covering all 1,064 segments.
- All model outputs remain machine evidence. The bindings support audit and replay of the
  process; they do not establish that translation wording is stable or human-correct.

## Cross-attempt comparison and nondeterminism boundary

The controlled comparison parses the first 198 non-empty rows from each attempt, requires the
same ordered segment IDs and Hebrew-source hashes, and compares complete row objects without
emitting Hebrew or English text.

| Measure | Result |
| --- | ---: |
| Compared rows | 198 |
| Exact row matches | 152 |
| Changed rows | 46 |
| Attempt 01 partial SHA-256 | `D258060249CEFDA4F18F727FED6A41D5AD4362E3EEF73A63ABC327645C8B216E` |
| Attempt 02 complete SHA-256 | `E163DC80783C2AECE0467FAA2456D0536BA950001D917A6C25B4D3013C8DC25B` |

Both event ledgers support partial parameter comparability, but their generator script hashes
differ. Therefore, provenance is auditable while output stability is not established. The 46
changed rows require bilingual human review and cannot be promoted to direct quotations.

## Private package and gate state

- Reviewed builder commit: `534da4aab609ab40c0ef5a7672b7af14ddcd031d`.
- Private package alias: `PRIVATE_EVIDENCE/packages/aug12-machine-evidence-v3`.
- Private source-provenance SHA-256:
  `B42BFB65EFA28A8AB123859E0994E91F453EEE48ABDCC74C655535FBC393B125`.
- Local deterministic package check: pass; exact inventory: ten regular files.
- Human-review templates: 1,280 records per reviewer (1,064 segments, 215 gaps, and one full
  timeline record).
- Human-reviewed records: `0/1,280` per reviewer; adjudications: `0`; reviewed media:
  `0/3,224.448` seconds.
- Independent adversarial review of v3: pass for machine-only preliminary evidence; report SHA-256
  `CC3683A2B861CBEA39D498279371E8B42BBE4BA15A83389FD3E37684C3FC18F5`.
  The earlier append-only v1 and v2 packages remain immutable and retain their own commit- and
  provenance-bound histories; neither is silently replaced by v3.

No closure certificate is permitted until two distinct reviewers complete the full record, a
distinct adjudicator resolves every disagreement, supervisor decisions are dispositioned, and
external delivery/acceptance evidence exists.
