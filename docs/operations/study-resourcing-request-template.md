# Study 2/3 Resourcing and Recruitment-Control Pack

Last updated: 2026-08-19

Status: **internal draft. Do not send until the applicable ethics/IRB, data-access, confidentiality,
and compensation/acknowledgment conditions are determined and the placeholders are completed.**

Source: `docs/research/phd-proposal/chapter-4-research-methodology.md` §§4.5–4.6 and
`docs/research/phd-proposal/three-study-contract.md`.

## 1. Roles that remain unassigned

### Study 2 — independent implementer

Purpose: test implementation-independence of the governed-judgment contract.

The person must not have designed the contract or the reference implementation. The required task is
to implement or adapt a small variant from the published specification, run the conformance suite,
and document ambiguities or hidden assumptions. A person who only reviews Ali's implementation can
support design review, but cannot satisfy the independent-implementation claim.

Minimum competence:

- ability to understand a structured data/schema contract;
- ability to implement or configure a small test variant in the selected language/tooling;
- ability to run an executable test suite and document failures;
- no prior authorship of the contract being tested;
- no unresolved conflict of interest that would compromise independence.

### Study 3 — two independent raters

Purpose: estimate whether the transfer-eligibility procedure can be applied consistently.

The two raters independently apply the frozen procedure to the same source-judgment/target-context
pairs. They select `Eligible`, `Eligible with adaptation`, `Blocked`, or `Undetermined` and record
the driving reason/dimension. Ratings remain blind to each other until the primary agreement
analysis is frozen.

Minimum competence:

- familiarity with the selected guideline-operationalization context;
- ability to follow a defined decision procedure rather than provide unconstrained expert opinion;
- independence from the procedure's design and from the other rater's decisions;
- completion of the same training and calibration exercise;
- no unresolved conflict of interest.

Domain expertise required for the final task must be fixed in the protocol. Software/modeling and
medical raters are not interchangeable merely because both can follow instructions.

## 2. Mandatory pre-outreach checklist

- [ ] Study purpose, task, estimated duration, schedule, and inclusion criteria are written.
- [ ] Applicable University of Haifa ethics/IRB determination is recorded: approval, exemption, or
      documented determination that the activity is not human-subject research.
- [ ] Data owner and data-access conditions are recorded.
- [ ] No restricted student, organizational, or medical data will be sent through ordinary email or
      stored in the public repository.
- [ ] Approved working environment and file-transfer method are defined.
- [ ] Confidentiality, retention, deletion, and publication/quotation rules are defined.
- [ ] Compensation, reimbursement, volunteer status, or acknowledgment policy is stated accurately.
- [ ] Conflict-of-interest and independence conditions are defined.
- [ ] Training and support materials are ready.
- [ ] Contact person for questions or withdrawal is identified.
- [ ] Iris and Arnon have approved or corrected the role description and study timing where required.

No person is considered recruited, assigned, or committed before these controls pass and the person
explicitly agrees.

## 3. Study 2 outreach draft — independent implementer

**Subject:** Request for an independent implementation task in a doctoral research proposal study

Hello [Name],

I am preparing a doctoral research proposal under the supervision of Iris Reinhartz-Berger and
Arnon Sturm. One study defines a system-independent contract for recording and governing human
judgment in an agentic assessment workflow. I am looking for an independent implementer who did
not design the contract or its reference implementation.

The proposed task is to [implement/configure a small variant from the supplied specification], run
the provided conformance suite, and document any ambiguity, missing requirement, or unexpected
failure. The task is expected to take approximately [duration] during [date range]. The required
technical background is [skills/tools]. Training and a short orientation will be provided before
the task.

The task will use [public/synthetic/approved controlled] material only. Work will take place in
[approved environment]. The confidentiality and data-handling requirements are [requirements].
[Compensation/reimbursement/volunteer and acknowledgment statement]. Participation is voluntary,
and you may stop before submitting the task without penalty, subject to the final approved study
information.

Would you be willing to receive the formal task information after the applicable study and ethics
conditions are confirmed? An expression of interest at this stage is not a commitment.

Thank you,

Ali Hamed

### Study 2 fields to complete before sending

| Field | Required entry |
| --- | --- |
| Recipient | Specific person |
| Required technical skills | — |
| Estimated duration | — |
| Date range | — |
| Approved data class | — |
| Approved environment | — |
| Confidentiality/retention terms | — |
| Compensation or acknowledgment | — |
| Ethics/IRB determination ID/date | — |
| Supervisor approval/reference | — |

## 4. Study 3 outreach draft — independent rater

Send a separate message to each candidate; do not place the two candidates in one shared recipient
list.

**Subject:** Request to serve as an independent rater in a doctoral research proposal study

Hello [Name],

I am preparing a doctoral research proposal under the supervision of Iris Reinhartz-Berger and
Arnon Sturm. One study evaluates a defined procedure for deciding whether a previously recorded
judgment may be used in a new guideline-operationalization context.

The proposed task is to independently review [number] source-judgment/target-context pairs and, for
each pair, select one of four procedure-defined states: `Eligible`, `Eligible with adaptation`,
`Blocked`, or `Undetermined`. You will also record the specific rule or context dimension that drove
the decision. This is an evaluation of the procedure's reliability; it is not a request for
free-form panel consensus. Ratings will remain blind to the other rater until the independent
analysis is frozen.

The task is expected to take approximately [duration] during [date range]. The required domain
background is [software/modeling or approved medical competence]. A shared orientation and
calibration exercise will be provided, and the calibration examples will not be part of the scored
set.

The task will use [public/synthetic/approved controlled] material only and will take place in
[approved environment]. The confidentiality and data-handling requirements are [requirements].
[Compensation/reimbursement/volunteer and acknowledgment statement]. Participation is voluntary,
and you may stop before submitting the task without penalty, subject to the final approved study
information.

Would you be willing to receive the formal task information after the applicable study and ethics
conditions are confirmed? An expression of interest at this stage is not a commitment.

Thank you,

Ali Hamed

### Study 3 fields to complete before sending

| Field | Required entry |
| --- | --- |
| Recipient | Specific person; one message per candidate |
| Required domain competence | — |
| Number of scored pairs | — |
| Estimated duration | — |
| Date range | — |
| Training/calibration plan | — |
| Approved data class | — |
| Approved environment | — |
| Confidentiality/retention terms | — |
| Compensation or acknowledgment | — |
| Ethics/IRB determination ID/date | — |
| Supervisor approval/reference | — |

## 5. Recording responses safely

Do not place real participant names, personal email addresses, consent records, or restricted study
materials in this public repository without explicit permission and a valid data-governance basis.
Use an approved private participant log and coded identifiers where appropriate.

The public decision/change log may record only a non-identifying status such as:

```text
Study 2 independent implementer: candidate identified / invited / agreed / declined / pending
Study 3 raters: 0 of 2 / 1 of 2 / 2 of 2 roles agreed
Ethics/data determination: pending / approved / exempt / not-human-subject determination recorded
```

The private record, if authorized, should contain the person's identity, role, contact date,
response, approved information sheet/consent state, conflict declaration, and withdrawal status.

## 6. Fallback if roles are not filled

- Study 2 may report reference-implementation conformance and the implementation-independence gap;
  it may not claim independent implementation validation.
- Study 3 may report the procedure and exact rater/evidence block; it may not report inter-rater
  reliability, target benefit, or safe transfer.
- Missing people must remain visible as a limitation rather than being replaced with fabricated
  names, AI-generated ratings, or author ratings described as independent.
