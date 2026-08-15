# Supervisor meeting — 2026-08-12, 09:02–09:56 (Iris Reinhartz-Berger, Arnon Sturm, Ali Hamed)

**Source:** `artifacts/meetings/2026-08-12-iris-arnon/machine-transcript.txt` (git-ignored),
53.7 min, Hebrew, transcribed locally with faster-whisper `large-v3-turbo`.

> **Provenance caveat, and it matters.** This is a *machine* transcript with **no speaker
> diarisation**. Attributions below are this record's inference from conversational context,
> not verified speech. Nothing here is a supervisor-approved decision until Ali confirms it.
> Do not quote any line as attributed speech.

Zoom chat (`chat.txt`) captured three shared items, which *are* verbatim:

| Time | From | Item |
| --- | --- | --- |
| 09:42 | Ali | `https://aclanthology.org/2026.findings-acl.1811/` |
| 09:48 | Iris | `https://github.com/HenryPengZou/Awesome-Human-Agent-Collaboration-Interaction-Systems` |
| 09:55 | Arnon | `arnon.sturm@gmail.com` |

---

## 1. The two chapters to start writing now

Opening item, attributed to Iris: two central chapters are still unwritten and should move
from thinking to **active writing**.

| Chapter | State per the record | Direction given |
| --- | --- | --- |
| Literature review | Five queries drafted, not executed | Check the queries against the research questions; then structure the chapter |
| Research methodology | Not started | Start *writing* it, not just thinking about it |

An observation attributed to Iris: the chapter plan does not yet show where **software
engineering** and the **medical** context enter. She expects both to appear.

## 2. What the literature review must be — the core directive

This is the substantive guidance of the meeting, and it reshapes the review.

- **The review precedes and justifies the gaps.** Attributed to Iris: this chapter "gives us
  the logic toward the gaps" — it must justify that a gap exists, and the gap lives **in the
  problem world, not the solution world**.
- **Focus on the research questions.** Some collected sources are old (variability types,
  software product lines, conformance) or off-question. The review should concentrate on
  literature bearing on the RQs, to show that nothing already answers them.
- **Separate enabling technology from the review.** Neural-network / LLM-infrastructure
  sources may appear later as references for *how* something is built, but they are **not the
  literature review**.
- **The centre of gravity — attributed to Iris:** *human involvement in the context of agentic
  AI*, with or without the specific scenarios this project studies. Domain-independent.
- **A separate section may cover the scenarios** — guideline operationalization — and *there*
  the software-engineering and medical contexts are discussed.
- **Was the search exhaustive?** Asked directly: has Google Scholar been searched properly,
  rather than relying on LLMs and the team's own paper? This is unresolved and is exactly what
  executing `QL-01…QL-05` must answer.

### A recorded disagreement, left open

| Position | Attributed to |
| --- | --- |
| The main literature should come from **HCI / interaction** — start broad (human–machine interaction, including 2000s multi-agent interaction), then drill into the domains | Arnon |
| Agrees the review must justify the problem; **disagrees on HCI as the frame** — neither supervisor is an HCI researcher. Work published *in* HCI venues is in scope, but the organising principle should be human involvement × agentic AI. Many relevant works are not in classic HCI venues | Iris |

Both agree the review argues the **problem**, not the solution.

### Method suggested in the meeting

Attributed to Iris, and acted on in this session: give the umbrella RQ and the three
sub-questions to an AI assistant and ask it to *"divide the literature review section based on
these research questions, and suggest a query for Google Scholar for each section."*
**The per-section Google Scholar queries are still outstanding.**

## 3. Methodology chapter — each question becomes a study

Attributed to Iris and Arnon jointly:

- Each of the three sub-questions must become **a study**, and ultimately **three studies →
  three publications**.
- Per question, state **the research artifact** and **the methodology** that produces and
  evaluates it — explicitly "in the context of what you discussed in Penina's course".
- Add a sub-section stating the work will be tested in **two kinds of guideline scenario**:
  software-engineering/students, and medical.

This matches `docs/research/phd-proposal/three-study-contract.md`; that document is the right
skeleton for the chapter.

## 4. Medical track — three live options

| Option | State per the record |
| --- | --- |
| Soroka | Met; framework agreed. Data of interest: discharge-summary free text, medications table, injections table. Physician defining access |
| Maayanei HaYeshua | Met a physician and an administrative director (a nurse). Direction: **schizophrenia / mental health** — guidelines are general, and different physicians treat differently, so variability is expected to be high |
| Clalit | Meeting scheduled **2026-08-26**, Ali invited |
| MIMIC | Explicitly the **fallback** — the record calls it "plan D": open data, but **no domain expert** to say what is correct |

Note the mental-health direction is interesting for this research precisely because guideline
generality produces legitimate practitioner variation — the substantial/occasional distinction
in a clinical setting.

**This does not change the gate status.** The six medical entry gates remain **0/6** in the
repository record; these are meetings and intentions, not documented approvals.

## 5. Other items

- Another doctoral student (**Matan**) is adding a **user interface** to VEGO-AI for
  intervention — but *unstructured*: correction of wrong output, with no policy for when or
  how to intervene. He is also testing **local/private LLMs**. The record positions Ali's work
  as the *selective, governed* intervention, which is a useful separation to state explicitly.
- **Privacy constraint, newly explicit:** student work cannot be uploaded to ordinary hosted
  LLMs — the same constraint that applies in the medical setting. This affects tooling choices.
- A student group may prepare data for next year.
- **Recommendation letters:** Ali needs letters from both supervisors; he was to send details
  and a draft. Deadline referenced as the 15th.
- **Drive sharing failed.** Ali reports trying to share the Drive with Arnon and not
  succeeding; Arnon supplied `arnon.sturm@gmail.com` in the chat for that purpose. This is the
  concrete resolution of the long-open `A08-05` sharing item **for Arnon**.

---

## Actions arising

| ID | Action | Owner | State |
| --- | --- | --- | --- |
| `A0812-01` | Restructure the literature review around *human involvement × agentic AI*, with guideline-operationalization scenarios as a separate section | Ali | Done for the course presentation; chapter still to write |
| `A0812-02` | Produce a Google Scholar query per review subsection | Ali | **Open** |
| `A0812-03` | Execute `QL-01…QL-05` and answer whether the search is exhaustive | Ali | **Open — blocks every gap claim** |
| `A0812-04` | Write the methodology chapter: artifact + method per sub-question, plus the two-scenario subsection | Ali | **Open** |
| `A0812-05` | Re-share the Drive with `arnon.sturm@gmail.com` | Ali | **Open** |
| `A0812-06` | Send recommendation-letter details to both supervisors | Ali | **Open — deadline referenced as the 15th** |
| `A0812-07` | Attend/settle the Clalit meeting 2026-08-26 (coincides with the Plan A/B checkpoint) | Ali | Scheduled |
| `A08-01` | Verify the final RQ wording against Ali's own saved draft | Ali | **Still open** — a machine search of this workstation found no saved copy |

## Unchanged evidence gates

| Gate | Value |
| --- | --- |
| EXP-005 generalization-safe expert labels | **0 of 24** |
| Medical entry gates G1–G6 | **0 of 6** |
| Literature searches QL-01…QL-05 | **not executed** |
