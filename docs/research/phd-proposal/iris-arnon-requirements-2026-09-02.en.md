# Requirements from the 2026-09-02 supervisor call (English)

Source: `artifacts/meetings/2026-09-02-iris-arnon/transcript.he.txt` — 40.8 minutes, 829 segments,
machine transcription (faster-whisper large-v3-turbo, Hebrew) of
`audio1667567525.m4a` from the Zoom recording of Prof. Iris Reinhartz-Berger's personal meeting
room, 2026-09-02 09:05. Hebrew edition of this file:
`iris-arnon-requirements-2026-09-02.he.md`.

**Same standing caveat as the other call records.** This is a machine transcript with no verified
speaker diarization. Everything below is a reviewed paraphrase, not a verbatim quotation, and none
of it is a supervisor-confirmed decision until Ali checks it against his own memory of the call.
Attribution to Iris or to Arnon is inferred from context and turn-taking, and is marked
*(attribution uncertain)* wherever the transcript does not make the speaker unambiguous. Do not
present any line here as "Iris said, verbatim" or as formally approved.

Timestamps in brackets refer to positions in the transcript.

## The headline: three things are missing, in priority order

Attributed to Iris, opening the call and then explicitly ordering the three [00:44–01:34]:

1. **Preliminary results** — "what worries me most right now". This is the priority.
2. **Focus and detail of the studies** — whether each study is specified well enough.
3. **Presentation** — how many chapters, whether there is a related-work chapter, whether a summary
   table is needed. Explicitly labelled a presentation matter, to be handled after the first two.

A fourth, stated separately [00:10–00:23]: **lead the reader in.** Do not drop the literature on
the reader; organise it so that it leads into the studies.

## Hard deadlines, as agreed at the end of the call

| Due | Deliverable | Detail |
| --- | --- | --- |
| **Thu 2026-09-03**, by roughly 13:00–14:00 | **One page: the study design** | What you intend to do, what you intend to measure, why it answers research question 1 (and which sub-question), on which dataset, and the plan of the thing [28:26–28:53, 39:44] |
| **Sun 2026-09-06** | **Two pages: design plus results and conclusions** | The same page extended with the actual run, the results, and your conclusions [30:15–30:25] |
| **Wed 2026-09-09** | **Version 2 of the proposal** | All of Arnon's written comments addressed, plus the preliminary results integrated, plus whatever feedback comes back on the Sunday submission [29:05–29:55, 30:25–30:37] |

Iris explicitly allowed the work to be delivered in stages rather than all at once [28:10–28:17],
and committed to reading the one-pager quickly *because* it is one page [28:38].

The 2026-09-09 meeting will be **larger than usual** — it will include Iris's project group and
Hagit (described as the physician), with a short private meeting of the three of them beforehand
[29:07–29:26]. *(attribution uncertain on the exact participant list)*

## The single preliminary study — scope, narrowed decisively by Iris

This is the most important content in the call. Iris cut the scope down twice, and the final
version is much narrower than what Ali initially described.

**What the study must do** [25:15–25:46, 39:00–39:18]:
- **Demonstrate** — Iris stressed the word, contrasting it with *prove* — points at which human
  involvement could have improved the outcome.
- Show **how those points can be identified automatically**.
- It need not be a complete catalogue. Examples are enough.

**What the study must NOT attempt** [25:51–26:16, 31:14–31:43]:
- Not proving improvement, and not comparing accuracy. That would require domain experts, two
  experts might disagree, and it is a far more serious effort than one month allows.
- Not *how* to improve, and not *how* to approach the user. Only **when** to escalate.
- Iris, flatly: "You do not have users, and you will not have users this month." She will connect
  Ali to Matan for users later, but not for this.

**The one question the study answers** [32:45–32:56]: when do we escalate to the human. Iris
interrupted an expanding answer to say this is the *only* study for now.

**Method Iris accepts** [21:22–21:31]: a descriptive analysis, demonstrated on a specific case, not
necessarily an empirical study with people. "Personally I think that is enough for the proposal."

**Simulating the humans** [12:42–13:45]: real participants are out of reach this month, but the
three of them can stand in as the involved humans, and interventions can be injected at chosen
points — "suppose at this point we intervene in this way". Iris noted Arnon had done exactly this
kind of thing the previous week. *(attribution uncertain)*

## Data

- Iris is **sceptical of synthetic data** [19:38–19:44]: "I do not know what you mean by synthetic
  data, and I am not sure how right it is to use synthetic data right now."
- Use the **course examples instead** [19:47–20:10]: Cheers and ParkWise. There is a
  teaching-assistant / exercise index for them that can be treated as ground truth in some sense.
- Ali asked for synthetic expert answers to serve as ground truth [19:03–19:21]; that request was
  not granted, and the course data was offered in its place.
- Iris also noted plainly [37:14–37:17] that **the ground truth is not available** for agent output,
  so identification may have to be partly manual at this stage.

## Candidate escalation triggers discussed

Raised by Iris as a possibility [32:00–32:03]: **confidence levels**.

Offered by Ali [33:08–33:54], three signals he says he already uses to choose intervention points:
1. Analysis of the modelling language itself.
2. A gap the agent identifies in the guidelines, where it produces no answer.
3. Several different candidate answers, or ambiguity in the data it consumed.

Also discussed: intervening **per stage** rather than once — at the template guidelines, the
inspector, and the domain guidelines, since the reason to intervene differs at each point
[33:59–34:08].

## The methodological criticism — the most important thing to absorb

Attributed to Iris [38:26–38:59], and delivered explicitly as generic rather than personal:

> This is a symptom common to researchers at the start of their path: you mix many things together,
> and you promise things you do not check. You say it will improve, but you did not actually check
> improvement. So we need to be careful: when we do research, we must bring evidence for everything.

The specific instance she pressed on [35:39–36:01]: Ali's claim about which agent to intervene at
is a **hypothetical analysis**, because the output of the alternative was never examined for quality
and no people were observed. Her question — "so how can you say it is better not to intervene at
agent 2 rather than agent 3?" — was not resolved in the call. Ali answered from the general
software-engineering principle that defects found earlier cost less to fix, so a correction made at
the language template does not propagate to the agent where 200 models are checked [36:01–36:28].
Iris did not accept this as evidence, and said the written page is where the question gets settled:
"we have question marks that I think it is your job tomorrow, and certainly by Sunday, to calm and
remove" [38:09–38:26].

Iris also stated directly [10:01–10:05] what she believes the current work amounts to: Ali has
**identified** places where involving a human is worthwhile, but has **not proved** — nor even
demonstrated — that it is correct. Ali agreed.

## A recorded difference between the supervisors: top-down versus bottom-up

Not resolved in the call, and worth carrying forward as an open question [36:33–37:31]:

- **Arnon wants top-down** — from the literature inward. *(attribution uncertain; Iris characterises
  Arnon's position here rather than Arnon stating it himself in this segment.)*
- **Iris was thinking bottom-up** — go and look at the models, see the problems, see what was
  identified, and from those find the point where the problems become visible.
- Iris closed the segment by allowing both: "you can go in both directions, from the data and from
  the numbers, to arrive at these things" [39:18–39:23].

## Arnon's position on sufficiency

Asked directly whether the narrowed study would be enough for preliminary results, Arnon judged it
**borderline but acceptable**, given the available time [27:06–27:31]. He agreed his own stronger
requirement is right for the long term but not for the current timeframe.

Separately, and earlier, Arnon's substantive objection [10:41–11:05, 11:34–11:51]: what exists
looks "very general"; the architecture is fine but it is a step on the way to demonstrating results,
not the result itself; and a reader of a proposal expects to see analytical ability, even
preliminary — "and here we are not demonstrating that in the proposal". *(attribution uncertain on
some of these lines.)*

## Scope correction: this is a proposal, not the course deliverable

Attributed to Iris [02:46–03:05, 15:17–15:58]. Ali referred to the work as a literature survey and
to Prof. Penina's course, where presenting results the same way was received badly. Iris drew the
line: the course had a different purpose, which was to show the literature. A **thesis proposal**
expects a detailed plan, feasibility, **and initial results**. The literature survey is one central
component of the proposal, but alongside it sit motivation, demonstration, what the studies are,
and preliminary results — and it is those that were not met.

## Standing actions carried out of the call

| ID | Action | Owner | Status |
| --- | --- | --- | --- |
| A0902-01 | One-page study design: what will be done, what will be measured, which research question it answers, on which dataset | Ali | Due Thu 2026-09-03 ~13:00 |
| A0902-02 | Two pages: the same design plus the run, results and conclusions | Ali | Due Sun 2026-09-06 |
| A0902-03 | Proposal version 2, addressing all of Arnon's comments and integrating the preliminary results | Ali | Due Wed 2026-09-09 |
| A0902-04 | Continue working through Arnon's written comments in parallel with the above | Ali | Ongoing |
| A0902-05 | Send Arnon specific questions by email where his comments are unclear | Ali | Open — Ali said he had already made a pass on the abstract/introduction and would send questions [40:19–40:33] |
| A0902-06 | Provide comments on the Thursday design page before Ali runs the study | Iris, Arnon | Open [28:53–28:59] |
| A0902-07 | Connect Ali to Matan so that real users become available — explicitly later, not this month | Iris | Deferred [31:43–31:49] |

## What this call does not change

The medical route, the six entry gates, EXP-005 labels, and the literature query families were not
discussed in this call and their status is unchanged. Nothing here should be read as approving the
proposal, the research-question wording, or any artifact boundary. Iris's closing framing was that
if the three of them can leave the meeting with a plan, the position is good [14:38–14:48] — a plan,
not an approval.
