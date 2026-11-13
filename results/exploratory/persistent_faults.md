# Persistent faults: the same fault on all three attempts

_Exploratory, post-review (v1.2). Not pre-specified; the frozen v1.1.1 core tables remain the record._

Scenarios in scenarios/exploratory/PF*.json use the option `retry_fault: copy_first`, so every retry repeats attempt 1's fault (fix for review item H3: in the frozen matrix every retry is nominal). Cell: effects at F, belief at H, dispatch times; flags DUP, FALSE-FAIL, FALSE-COMPLETE.

## PF1: persistent lost ack, L = 1

Every attempt commits one tick after arrival; its response and webhooks are lost. L = 1.

| policy | contract 1 | contract 2 |
|---|---|---|
| A | 3 effects, failed, a1@0 a2@5 a3@10 **DUP FALSE-FAIL** | 1 effects, failed, a1@0 a2@5 a3@10 **FALSE-FAIL** |
| B | 1 effects, complete, a1@0 | 1 effects, complete, a1@0 |
| Bw | 1 effects, complete, a1@0 | 1 effects, complete, a1@0 |
| C | 1 effects, complete, a1@0 | 1 effects, complete, a1@0 |
| D | 1 effects, complete, a1@0 | 1 effects, complete, a1@0 |
| D+I (optional) | 1 effects, complete, a1@0 | 1 effects, complete, a1@0 |
| A-fk (ablation) | - | 3 effects, failed, a1@0 a2@5 a3@10 **DUP FALSE-FAIL** |
| ORACLE-S (state-probe reference, not a ceiling) | 1 effects, complete, a1@0 | 1 effects, complete, a1@0 |
| ORACLE-O (outcome-oracle reference) | 1 effects, complete, a1@0 | 1 effects, complete, a1@0 |

## PF2: persistent lost ack, L = never

Every attempt commits one tick after arrival; its response and webhooks are lost. L = never.

| policy | contract 1 | contract 2 |
|---|---|---|
| A | 3 effects, failed, a1@0 a2@5 a3@10 **DUP FALSE-FAIL** | 1 effects, failed, a1@0 a2@5 a3@10 **FALSE-FAIL** |
| B | 3 effects, failed, a1@0 a2@6 a3@12 **DUP FALSE-FAIL** | 1 effects, failed, a1@0 a2@6 a3@12 **FALSE-FAIL** |
| Bw | 3 effects, unresolved, a1@0 a2@21 a3@42 **DUP** | 1 effects, unresolved, a1@0 a2@21 a3@42 |
| C | 1 effects, unresolved, a1@0 | 1 effects, unresolved, a1@0 |
| D | 1 effects, unresolved, a1@0 | 1 effects, unresolved, a1@0 |
| D+I (optional) | 1 effects, unresolved, a1@0 | 1 effects, unresolved, a1@0 a2@6 a3@16 |
| A-fk (ablation) | - | 3 effects, failed, a1@0 a2@5 a3@10 **DUP FALSE-FAIL** |
| ORACLE-S (state-probe reference, not a ceiling) | 1 effects, complete, a1@0 | 1 effects, complete, a1@0 |
| ORACLE-O (outcome-oracle reference) | 1 effects, complete, a1@0 | 1 effects, complete, a1@0 |

## PF3: persistent lost request

Every request is lost before arrival. L = 1.

| policy | contract 1 | contract 2 |
|---|---|---|
| A | 0 effects, failed, a1@0 a2@5 a3@10 | 0 effects, failed, a1@0 a2@5 a3@10 |
| B | 0 effects, failed, a1@0 a2@6 a3@12 | 0 effects, failed, a1@0 a2@6 a3@12 |
| Bw | 0 effects, unresolved, a1@0 a2@21 a3@42 | 0 effects, unresolved, a1@0 a2@21 a3@42 |
| C | 0 effects, unresolved, a1@0 | 0 effects, unresolved, a1@0 |
| D | 0 effects, unresolved, a1@0 | 0 effects, unresolved, a1@0 |
| D+I (optional) | 0 effects, unresolved, a1@0 | 0 effects, unresolved, a1@0 a2@6 a3@16 |
| A-fk (ablation) | - | 0 effects, failed, a1@0 a2@5 a3@10 |
| ORACLE-S (state-probe reference, not a ceiling) | 0 effects, failed, a1@0 a2@5 a3@10 | 0 effects, failed, a1@0 a2@5 a3@10 |
| ORACLE-O (outcome-oracle reference) | 0 effects, failed, a1@0 a2@5 a3@10 | 0 effects, failed, a1@0 a2@5 a3@10 |

## PF4: persistent abort

Every attempt is accepted and aborts two ticks after arrival; response lost; the `aborted` webhook arrives two ticks after the abort. L = 1.

| policy | contract 1 | contract 2 |
|---|---|---|
| A | 0 effects, failed, a1@0 a2@5 a3@5 | 0 effects, failed, a1@0 a2@5 a3@5 |
| B | 0 effects, failed, a1@0 a2@6 a3@6 | 0 effects, failed, a1@0 a2@6 a3@6 |
| Bw | 0 effects, unresolved, a1@0 a2@21 a3@42 | 0 effects, unresolved, a1@0 a2@21 a3@42 |
| C | 0 effects, failed, a1@0 | 0 effects, failed, a1@0 |
| D | 0 effects, failed, a1@0 a2@5 a3@10 | 0 effects, failed, a1@0 a2@5 a3@10 |
| D+I (optional) | 0 effects, failed, a1@0 a2@5 a3@10 | 0 effects, unresolved, a1@0 a2@5 a3@6 |
| A-fk (ablation) | - | 0 effects, failed, a1@0 a2@5 a3@5 |
| ORACLE-S (state-probe reference, not a ceiling) | 0 effects, failed, a1@0 a2@5 a3@10 | 0 effects, failed, a1@0 a2@5 a3@10 |
| ORACLE-O (outcome-oracle reference) | 0 effects, failed, a1@0 a2@5 a3@10 | 0 effects, failed, a1@0 a2@5 a3@10 |

