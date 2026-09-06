# Study 1/Study 2 canonical draft selection

**Review date:** 2026-09-06
**Evidence class:** implementation/protocol metadata only; no scientific run.

The repository was fetched before selection. At review time:

| Ref | State | SHA |
|---|---|---|
| `origin/main` | current base | `c34d3954b5e080d090017d2ea655d454d75a6b92` |
| PR #34 | open, draft | `55ff48a0e0014979c538e03452444a35ae7c50a7` |
| PR #35 | open, draft | `8561aa0b9e241255f0f2346ac85180758f3ccb53` |
| PR #38 | open, draft | `a976494a624391efb0fb96e8f769512f52f52af0` |
| PR #39 | open, draft | `5232475a97109de4f82aad451ed82f23370cd1e9` |
| PR #40 | open, draft | `43b582040ac1780624121f67e8facd4ddfaddc7e` |
| PR #41 | open, draft | `63da0105f25207e3cc6e67bb3ec499652d65124c` |
| PR #42 | open, draft | `de65a57d5ca7289cc6032baa7cc797499fdc6812` |

The open Study 1/Study 2 set also includes PRs #34, #35, #39 and #40. They
remain independent review candidates and were not merged into this branch.
PR #41 descends from PR #38 (the merge base is PR #38's head), so it is the
canonical Study 1 closure and combined-study starting point. The earlier
overlap audit found 79 changed files in PR #38 and 69 in PR #41, with the
shared history preserved rather than merged again.

PR #42 is a divergent Study 2-only branch from `origin/main`; it is not an
ancestor of PR #41. Its reusable ON/OFF contract, schemas, fixture runner and
tests were ported selectively into this branch. No broad PR merge was used,
and no protected VEGO runtime, Detector-v1, v1.0.1 or v1.0.2 file was changed.

The resulting local implementation branch is
`study1/study1-study2-traceability`. It carries the PR #41 ancestry plus
evidence-bound Study 1 recovery/traceability and a dependency-injected Study 2
runner. The branch is not a merge or approval of either open PR; independent
review and human decisions remain required.
