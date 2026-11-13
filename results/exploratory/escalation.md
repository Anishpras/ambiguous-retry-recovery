# Escalation detail: what would resolve each unresolved operation

_Exploratory, post-review (v1.2). Not pre-specified; the frozen v1.1.1 core tables remain the record._

For every operation whose belief at H is `unresolved`, the attempts the client could not close (no authoritative negative observed) and the evidence that would resolve it, given the hidden truth. Full list: escalation.csv.

| source | policy | evidence needed (per open attempt) | count |
|---|---|---|---|
| core | C | correlated positive | 4 |
| core | C | correlated positive after H / longer horizon | 2 |
| core | C | terminal negative or in-flight bound | 2 |
| core | D | correlated positive | 4 |
| core | D | correlated positive after H / longer horizon | 2 |
| core | D | terminal negative or in-flight bound | 2 |
| core | D+I (optional) | correlated positive | 2 |
| core | D+I (optional) | correlated positive after H / longer horizon | 2 |
| core | D+I (optional) | terminal negative or in-flight bound | 1 |
| core | ORACLE-O (outcome-oracle reference) | correlated positive after H / longer horizon | 2 |
| grid | C | correlated positive | 8 |
| grid | C | correlated positive after H / longer horizon | 12 |
| grid | C | terminal negative or in-flight bound | 12 |
| grid | D | correlated positive | 8 |
| grid | D | correlated positive after H / longer horizon | 12 |
| grid | D | terminal negative or in-flight bound | 12 |
| grid | D+I (optional) | correlated positive | 4 |
| grid | D+I (optional) | correlated positive after H / longer horizon | 12 |
| grid | D+I (optional) | terminal negative or in-flight bound | 6 |
| grid | ORACLE-O (outcome-oracle reference) | correlated positive after H / longer horizon | 12 |
| persistent_fault | Bw | correlated positive | 4 |
| persistent_fault | Bw | in-flight time bound | 4 |
| persistent_fault | Bw | terminal negative or in-flight bound | 6 |
| persistent_fault | C | correlated positive | 2 |
| persistent_fault | C | terminal negative or in-flight bound | 2 |
| persistent_fault | D | correlated positive | 2 |
| persistent_fault | D | terminal negative or in-flight bound | 2 |
| persistent_fault | D+I (optional) | correlated positive | 2 |
| persistent_fault | D+I (optional) | in-flight time bound | 3 |
| persistent_fault | D+I (optional) | terminal negative or in-flight bound | 4 |

Core matrix, every unresolved operation:

| contract | policy | scenario/op | open attempts | evidence that resolves it | hidden truth |
|---|---|---|---|---|---|
| 1 | C | S08/op-1 | a1 | correlated positive for a1 | a1 committed@2 |
| 1 | C | S09/op-1 | a1 | terminal negative or in-flight time bound for a1 | a1 never_arrived |
| 1 | C | S10/op-1 | a1 | correlated positive for a1 after t=90 (or a longer horizon) | a1 commits_after_H@90 |
| 1 | C | S11/op-1 | a1 | correlated positive for a1 | a1 committed@2 |
| 1 | D | S08/op-1 | a1 | correlated positive for a1 | a1 committed@2 |
| 1 | D | S09/op-1 | a1 | terminal negative or in-flight time bound for a1 | a1 never_arrived |
| 1 | D | S10/op-1 | a1 | correlated positive for a1 after t=90 (or a longer horizon) | a1 commits_after_H@90 |
| 1 | D | S11/op-1 | a1 | correlated positive for a1 | a1 committed@2 |
| 1 | D+I | S08/op-1 | a1 | correlated positive for a1 | a1 committed@2 |
| 1 | D+I | S09/op-1 | a1 | terminal negative or in-flight time bound for a1 | a1 never_arrived |
| 1 | D+I | S10/op-1 | a1 | correlated positive for a1 after t=90 (or a longer horizon) | a1 commits_after_H@90 |
| 1 | D+I | S11/op-1 | a1 | correlated positive for a1 | a1 committed@2 |
| 1 | ORACLE-O | S10/op-1 | a1 | correlated positive for a1 after t=90 (or a longer horizon) | a1 commits_after_H@90 |
| 2 | C | S08/op-1 | a1 | correlated positive for a1 | a1 committed@2 |
| 2 | C | S09/op-1 | a1 | terminal negative or in-flight time bound for a1 | a1 never_arrived |
| 2 | C | S10/op-1 | a1 | correlated positive for a1 after t=90 (or a longer horizon) | a1 commits_after_H@90 |
| 2 | C | S11/op-1 | a1 | correlated positive for a1 | a1 committed@2 |
| 2 | D | S08/op-1 | a1 | correlated positive for a1 | a1 committed@2 |
| 2 | D | S09/op-1 | a1 | terminal negative or in-flight time bound for a1 | a1 never_arrived |
| 2 | D | S10/op-1 | a1 | correlated positive for a1 after t=90 (or a longer horizon) | a1 commits_after_H@90 |
| 2 | D | S11/op-1 | a1 | correlated positive for a1 | a1 committed@2 |
| 2 | D+I | S10/op-1 | a1 | correlated positive for a1 after t=90 (or a longer horizon) | a1 commits_after_H@90 |
| 2 | ORACLE-O | S10/op-1 | a1 | correlated positive for a1 after t=90 (or a longer horizon) | a1 commits_after_H@90 |
