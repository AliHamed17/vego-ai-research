# Executive Summary: Study 2 Prospective Paired Run `S2P-LIVE-20260908T192135Z`

**Evidence class:** PROSPECTIVE EMPIRICAL EVIDENCE. One prospective paired run of the VEGO-AI four-agent workflow (ON) against a matched direct single-model workflow (OFF) on 12 seeded cases of the public Text2UML AirTravel frame (21 eligible), model gpt-5.6-luna, hard ceiling 6.00 USD.

## What happened

- Completion: ON 9/12 artifacts, OFF 12/12; both completed in 9 cases.
- Structural validity: ON 9/9 artifacts with a self-consistent coverage summary; OFF 7/12.
- Requests: ON 227 (of which 2 setting-level), OFF 12; total 240 of cap 267.
- Cost: ON 0.9029 USD, OFF 0.0530 USD; recorded total 0.9559 USD (upper bound 0.9780 USD with 1 in-flight request(s) charged at full reserve) against a 5.8241 USD reservation and a 6.00 USD ceiling.
- Time: ON 1712.78 s, OFF 238.696 s for the whole condition.
- Technical failures: ON 3, OFF 0; transport retries ON 0, OFF 0.
- Communication evidence: ON produced 16 recorded Q&A episodes (14 scientifically complete); OFF has none by design.
- Detector-v1 (ON only, reporting-only): STRONG_ALERT 13, EXCLUDED 2, WEAK_ALERT 1; cases with any candidate label: 0.75. Under OFF: NOT_APPLICABLE.
- Artifact structure differs by construction: ON artifacts carry 1-1 mapping rows per case (the Domain Advisor produced 1 reference guideline(s)) and 13-20 uncovered fragments (total 158: Domain Mistake 77, Alternative 75, Language Mistake 6); OFF, which receives no guideline list, derived 11-21 guidelines per case and flagged 2-6 fragments (total 42: Domain Mistake 18, Alternative 13, Language Mistake 11). Row counts are therefore not comparable as a quality measure.

## What this does and does not show

It shows how the two workflows behaved operationally on the same inputs under identical request policy. It does not show which produced better analyses, whether any Detector-v1 label is correct, or anything about human benefit; those are NOT_MEASURED until two independent raters score the blinded cards.

## Next step

Two raters score the 14 blinded cards with the Hebrew rubric; only then can agreement and any correctness-type statement be computed.
