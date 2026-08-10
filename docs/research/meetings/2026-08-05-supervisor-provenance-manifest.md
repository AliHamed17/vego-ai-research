# Provenance Manifest - 2026-08-05 Supervisor Meeting

| Field | Record |
| --- | --- |
| Date | 2026-08-05 |
| Format | Zoom recording (local, not cloud) |
| Recording duration | 00:56:33, from local Windows media metadata (`video1638342429.mp4`) |
| Participants evidenced by the conversation | Ali Hamed; Prof. Iris Reinhartz-Berger (addressed by name, `00:56:27`); Prof. Arnon (addressed directly, e.g. `00:11:01`, `00:16:23`) |
| Zoom chat log | `docs/chat1638342429.txt` - contains only the meeting topic line ("Variability Exploration via Guideline Operationalization and Agentic Intelligence"), no substantive chat content |
| Canonical recording (local only, gitignored) | `docs/video1638342429.mp4`, `docs/audio1638342429.m4a` |
| Canonical ASR | `docs/video1638342429.transcript.he.txt` (timestamped), `.srt` (subtitle-aligned), `.md` (provenance header + full text) - all gitignored, local only |
| ASR method | faster-whisper `mobiuslabsgmbh/faster-whisper-large-v3-turbo`, Hebrew, local CPU `int8` |
| ASR generated | 2026-08-10, wall time ~2826s for 3394s of audio |
| Segments | 2347 |
| Language detected | Hebrew, probability 1.0 |
| Speaker diarization | None; speaker identity below is inferred from turn order, direct address ("Arnon, do you have comments"), and self-reference, exactly as in the 2026-07-01 record |
| English rendering | `docs/video1638342429.transcript.en.md` - a paraphrase/translation of the Hebrew ASR, organized by topic with timestamp anchors rather than a mechanical line-by-line rendering of all 2347 fragments (many are single-word ASR artifacts of live, fast, overlapping dictation). **Not a verified translation or quotation.** |
| Meeting record | `docs/research/meetings/2026-08-05-supervisor-meeting.md` |
| Human review state | Pending. Do not treat any wording below - especially the live-edited research-question text - as final or attributable until a Hebrew-speaking reviewer compares it against the recording, consistent with `ISS-022`. |

## Notable transcription conditions

- A meaningful stretch of the meeting (~`00:11:00`-`00:44:00`) is **live collaborative wordsmithing** of the thesis research questions: short interjections, half-sentences, and word-by-word dictated edits (including English phrases dictated inside Hebrew speech, apparently to be pasted into an AI assistant referred to as "Claude" for help refining the wording). This produces many single-word or few-word ASR segments. The **direction** of each edit is generally clear from context; the **exact final assembled sentence** is not fully reconstructable from the ASR alone and needs verification against the recording or against wherever Ali pasted the working draft.
- Some technical/English terms are transliterated inconsistently by the ASR (e.g. "ריוזבל" for "reusable", "אבלואציה" for "evaluation") - resolved by context in the English rendering, flagged inline where ambiguous.

## Related evidence

- [Meeting record](2026-08-05-supervisor-meeting.md)
- `docs/video1638342429.transcript.he.txt` / `.srt` / `.md` - canonical Hebrew ASR (local only)
- `docs/video1638342429.transcript.en.md` - English rendering (local only)
- `docs/research/meetings/2026-08-05-supervisor-asr.he.metadata.json` - raw ASR run metadata
