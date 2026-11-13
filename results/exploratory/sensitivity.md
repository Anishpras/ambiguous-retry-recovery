# Sensitivity of the results to alternative rules

_Exploratory, post-review (v1.2). Not pre-specified; the frozen v1.1.1 core tables remain the record._

One row per alternative rule from the independent review (section 3). Each is a named option (arr/options.py) applied to every policy, contract, core scenario and grid schedule; options that only concern some policies leave the others unchanged. Cells read duplicates / exactly-once / unresolved at H / false failure / false complete, as counts of operations (core: 17 per contract; grid: 120). Bold = differs from the baseline row. Counts are over authored cases, not rates.

## baseline

v1.2 defaults: the frozen rules plus the v1.2 fixes. Options: `none`.

| policy | c1 core | c1 grid | c2 core | c2 grid |
|---|---|---|---|---|
| A | 12/5/0/0/0 | 90/30/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| B | 8/9/0/0/0 | 60/60/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| Bw | 3/14/0/0/0 | 27/93/0/0/0 | 0/17/0/1/0 | 0/120/0/6/0 |
| C | 0/14/4/0/0 | 0/114/16/0/0 | 0/14/4/0/0 | 0/114/16/0/0 |
| D | 1/15/4/0/0 | 0/114/16/0/0 | 1/15/4/0/0 | 0/114/16/0/0 |
| D+I (optional) | 1/15/4/0/0 | 0/114/16/0/0 | 1/16/1/0/0 | 0/120/6/0/0 |
| A-fk (ablation) | - | - | 12/5/0/0/0 | 90/30/0/0/0 |
| ORACLE-S (state-probe reference, not a ceiling) | 4/13/0/0/0 | 30/90/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| ORACLE-O (outcome-oracle reference) | 0/17/1/0/0 | 0/120/6/0/0 | 0/17/1/0/0 | 0/120/6/0/0 |

## status_lists_pending

status `not_found` lists pending attempts, and B and Bw re-read (every 5 ticks) instead of retrying while one is pending. Options: `reread_on_pending=True, status_lists_pending=True`.

| policy | c1 core | c1 grid | c2 core | c2 grid |
|---|---|---|---|---|
| A | 12/5/0/0/0 | 90/30/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| B | **5/12/1/0/0** | **40/80/3/0/0** | **1/16/1/0/0** | **0/120/3/3/0** |
| Bw | **2/15/1/0/0** | **15/105/4/0/0** | **0/17/1/0/0** | **0/120/4/2/0** |
| C | 0/14/4/0/0 | 0/114/16/0/0 | 0/14/4/0/0 | 0/114/16/0/0 |
| D | 1/15/4/0/0 | 0/114/16/0/0 | 1/15/4/0/0 | 0/114/16/0/0 |
| D+I (optional) | 1/15/4/0/0 | 0/114/16/0/0 | 1/16/1/0/0 | 0/120/6/0/0 |
| A-fk (ablation) | - | - | 12/5/0/0/0 | 90/30/0/0/0 |
| ORACLE-S (state-probe reference, not a ceiling) | 4/13/0/0/0 | 30/90/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| ORACLE-O (outcome-oracle reference) | 0/17/1/0/0 | 0/120/6/0/0 | 0/17/1/0/0 | 0/120/6/0/0 |

## webhooks_not_by_name

A, B, Bw treat `deferred` as progress and ignore failure webhooks once complete. Options: `deferred_is_progress=True, ignore_failure_webhooks_once_complete=True`.

| policy | c1 core | c1 grid | c2 core | c2 grid |
|---|---|---|---|---|
| A | **10/7/0/0/0** | 90/30/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| B | 8/9/0/0/0 | 60/60/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| Bw | 3/14/0/0/0 | 27/93/0/0/0 | 0/17/0/1/0 | 0/120/0/6/0 |
| C | 0/14/4/0/0 | 0/114/16/0/0 | 0/14/4/0/0 | 0/114/16/0/0 |
| D | 1/15/4/0/0 | 0/114/16/0/0 | 1/15/4/0/0 | 0/114/16/0/0 |
| D+I (optional) | 1/15/4/0/0 | 0/114/16/0/0 | 1/16/1/0/0 | 0/120/6/0/0 |
| A-fk (ablation) | - | - | **10/7/0/0/0** | 90/30/0/0/0 |
| ORACLE-S (state-probe reference, not a ceiling) | 4/13/0/0/0 | 30/90/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| ORACLE-O (outcome-oracle reference) | 0/17/1/0/0 | 0/120/6/0/0 | 0/17/1/0/0 | 0/120/6/0/0 |

## bw_without_C15

Bw issues its verify read even if already complete (the reply is still ignored once complete, revision v1.1.1). Options: `bw_skip_read_if_complete=False`.

| policy | c1 core | c1 grid | c2 core | c2 grid |
|---|---|---|---|---|
| A | 12/5/0/0/0 | 90/30/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| B | 8/9/0/0/0 | 60/60/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| Bw | 3/14/0/0/0 | 27/93/0/0/0 | 0/17/0/1/0 | 0/120/0/6/0 |
| C | 0/14/4/0/0 | 0/114/16/0/0 | 0/14/4/0/0 | 0/114/16/0/0 |
| D | 1/15/4/0/0 | 0/114/16/0/0 | 1/15/4/0/0 | 0/114/16/0/0 |
| D+I (optional) | 1/15/4/0/0 | 0/114/16/0/0 | 1/16/1/0/0 | 0/120/6/0/0 |
| A-fk (ablation) | - | - | 12/5/0/0/0 | 90/30/0/0/0 |
| ORACLE-S (state-probe reference, not a ceiling) | 4/13/0/0/0 | 30/90/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| ORACLE-O (outcome-oracle reference) | 0/17/1/0/0 | 0/120/6/0/0 | 0/17/1/0/0 | 0/120/6/0/0 |

## bw_without_C15_or_reply_guard

as above, and A, B, Bw act on status replies after completion (v1.0/v1.1 literal reading). Options: `bw_skip_read_if_complete=False, ignore_status_replies_once_complete=False`.

| policy | c1 core | c1 grid | c2 core | c2 grid |
|---|---|---|---|---|
| A | 12/5/0/0/0 | 90/30/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| B | 8/9/0/0/0 | **70/50/0/0/0** | 1/16/0/1/0 | 0/120/0/6/0 |
| Bw | **5/12/0/0/0** | **44/76/0/0/0** | 0/17/0/1/0 | 0/120/0/6/0 |
| C | 0/14/4/0/0 | 0/114/16/0/0 | 0/14/4/0/0 | 0/114/16/0/0 |
| D | 1/15/4/0/0 | 0/114/16/0/0 | 1/15/4/0/0 | 0/114/16/0/0 |
| D+I (optional) | 1/15/4/0/0 | 0/114/16/0/0 | 1/16/1/0/0 | 0/120/6/0/0 |
| A-fk (ablation) | - | - | 12/5/0/0/0 | 90/30/0/0/0 |
| ORACLE-S (state-probe reference, not a ceiling) | 4/13/0/0/0 | 30/90/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| ORACLE-O (outcome-oracle reference) | 0/17/1/0/0 | 0/120/6/0/0 | 0/17/1/0/0 | 0/120/6/0/0 |

## tau_5

Bw waits 5 ticks. Options: `wait_tau=5`.

| policy | c1 core | c1 grid | c2 core | c2 grid |
|---|---|---|---|---|
| A | 12/5/0/0/0 | 90/30/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| B | 8/9/0/0/0 | 60/60/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| Bw | **7/10/0/0/0** | **40/80/0/0/0** | **1/16/0/1/0** | 0/120/0/6/0 |
| C | 0/14/4/0/0 | 0/114/16/0/0 | 0/14/4/0/0 | 0/114/16/0/0 |
| D | 1/15/4/0/0 | 0/114/16/0/0 | 1/15/4/0/0 | 0/114/16/0/0 |
| D+I (optional) | 1/15/4/0/0 | 0/114/16/0/0 | 1/16/1/0/0 | 0/120/6/0/0 |
| A-fk (ablation) | - | - | 12/5/0/0/0 | 90/30/0/0/0 |
| ORACLE-S (state-probe reference, not a ceiling) | 4/13/0/0/0 | 30/90/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| ORACLE-O (outcome-oracle reference) | 0/17/1/0/0 | 0/120/6/0/0 | 0/17/1/0/0 | 0/120/6/0/0 |

## tau_10

Bw waits 10 ticks. Options: `wait_tau=10`.

| policy | c1 core | c1 grid | c2 core | c2 grid |
|---|---|---|---|---|
| A | 12/5/0/0/0 | 90/30/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| B | 8/9/0/0/0 | 60/60/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| Bw | **4/13/0/0/0** | **34/86/0/0/0** | 0/17/0/1/0 | 0/120/0/6/0 |
| C | 0/14/4/0/0 | 0/114/16/0/0 | 0/14/4/0/0 | 0/114/16/0/0 |
| D | 1/15/4/0/0 | 0/114/16/0/0 | 1/15/4/0/0 | 0/114/16/0/0 |
| D+I (optional) | 1/15/4/0/0 | 0/114/16/0/0 | 1/16/1/0/0 | 0/120/6/0/0 |
| A-fk (ablation) | - | - | 12/5/0/0/0 | 90/30/0/0/0 |
| ORACLE-S (state-probe reference, not a ceiling) | 4/13/0/0/0 | 30/90/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| ORACLE-O (outcome-oracle reference) | 0/17/1/0/0 | 0/120/6/0/0 | 0/17/1/0/0 | 0/120/6/0/0 |

## tau_20

Bw waits 20 ticks. Options: `wait_tau=20`.

| policy | c1 core | c1 grid | c2 core | c2 grid |
|---|---|---|---|---|
| A | 12/5/0/0/0 | 90/30/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| B | 8/9/0/0/0 | 60/60/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| Bw | 3/14/0/0/0 | **26/94/0/0/0** | **0/17/1/0/0** | **0/120/6/0/0** |
| C | 0/14/4/0/0 | 0/114/16/0/0 | 0/14/4/0/0 | 0/114/16/0/0 |
| D | 1/15/4/0/0 | 0/114/16/0/0 | 1/15/4/0/0 | 0/114/16/0/0 |
| D+I (optional) | 1/15/4/0/0 | 0/114/16/0/0 | 1/16/1/0/0 | 0/120/6/0/0 |
| A-fk (ablation) | - | - | 12/5/0/0/0 | 90/30/0/0/0 |
| ORACLE-S (state-probe reference, not a ceiling) | 4/13/0/0/0 | 30/90/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| ORACLE-O (outcome-oracle reference) | 0/17/1/0/0 | 0/120/6/0/0 | 0/17/1/0/0 | 0/120/6/0/0 |

## tau_30

Bw waits 30 ticks. Options: `wait_tau=30`.

| policy | c1 core | c1 grid | c2 core | c2 grid |
|---|---|---|---|---|
| A | 12/5/0/0/0 | 90/30/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| B | 8/9/0/0/0 | 60/60/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| Bw | 3/14/0/0/0 | **16/104/0/0/0** | **0/17/1/0/0** | **0/120/6/0/0** |
| C | 0/14/4/0/0 | 0/114/16/0/0 | 0/14/4/0/0 | 0/114/16/0/0 |
| D | 1/15/4/0/0 | 0/114/16/0/0 | 1/15/4/0/0 | 0/114/16/0/0 |
| D+I (optional) | 1/15/4/0/0 | 0/114/16/0/0 | 1/16/1/0/0 | 0/120/6/0/0 |
| A-fk (ablation) | - | - | 12/5/0/0/0 | 90/30/0/0/0 |
| ORACLE-S (state-probe reference, not a ceiling) | 4/13/0/0/0 | 30/90/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| ORACLE-O (outcome-oracle reference) | 0/17/1/0/0 | 0/120/6/0/0 | 0/17/1/0/0 | 0/120/6/0/0 |

## in_progress_is_wait

A, B, Bw treat `in_progress` as 'wait', not as a failure signal. Options: `in_progress_is_wait=True`.

| policy | c1 core | c1 grid | c2 core | c2 grid |
|---|---|---|---|---|
| A | 12/5/0/0/0 | 90/30/0/0/0 | **1/16/1/0/0** | **0/120/6/0/0** |
| B | 8/9/0/0/0 | 60/60/0/0/0 | **1/16/1/0/0** | **0/120/6/0/0** |
| Bw | 3/14/0/0/0 | 27/93/0/0/0 | **0/17/1/0/0** | **0/120/6/0/0** |
| C | 0/14/4/0/0 | 0/114/16/0/0 | 0/14/4/0/0 | 0/114/16/0/0 |
| D | 1/15/4/0/0 | 0/114/16/0/0 | 1/15/4/0/0 | 0/114/16/0/0 |
| D+I (optional) | 1/15/4/0/0 | 0/114/16/0/0 | 1/16/1/0/0 | 0/120/6/0/0 |
| A-fk (ablation) | - | - | 12/5/0/0/0 | 90/30/0/0/0 |
| ORACLE-S (state-probe reference, not a ceiling) | 4/13/0/0/0 | 30/90/0/0/0 | 1/16/0/1/0 | 0/120/0/6/0 |
| ORACLE-O (outcome-oracle reference) | 0/17/1/0/0 | 0/120/6/0/0 | 0/17/1/0/0 | 0/120/6/0/0 |

## abort_record_replays_failure

contract 2: an aborted record replays the failure (later attempts with the key are refused) instead of being released. Options: `abort_record=replay_failure`.

| policy | c1 core | c1 grid | c2 core | c2 grid |
|---|---|---|---|---|
| A | 12/5/0/0/0 | 90/30/0/0/0 | **0/15/0/1/0** | 0/120/0/6/0 |
| B | 8/9/0/0/0 | 60/60/0/0/0 | **0/15/0/1/0** | 0/120/0/6/0 |
| Bw | 3/14/0/0/0 | 27/93/0/0/0 | **0/15/0/1/0** | 0/120/0/6/0 |
| C | 0/14/4/0/0 | 0/114/16/0/0 | 0/14/4/0/0 | 0/114/16/0/0 |
| D | 1/15/4/0/0 | 0/114/16/0/0 | **0/14/4/0/0** | 0/114/16/0/0 |
| D+I (optional) | 1/15/4/0/0 | 0/114/16/0/0 | **0/15/1/0/0** | 0/120/6/0/0 |
| A-fk (ablation) | - | - | 12/5/0/0/0 | 90/30/0/0/0 |
| ORACLE-S (state-probe reference, not a ceiling) | 4/13/0/0/0 | 30/90/0/0/0 | **0/15/0/1/0** | 0/120/0/6/0 |
| ORACLE-O (outcome-oracle reference) | 0/17/1/0/0 | 0/120/6/0/0 | **0/15/1/0/0** | 0/120/6/0/0 |

## persistent_faults

retries copy attempt 1's fault instead of being nominal. Options: `retry_fault=copy_first`.

| policy | c1 core | c1 grid | c2 core | c2 grid |
|---|---|---|---|---|
| A | **11/2/0/4/0** | **90/24/0/24/0** | **1/12/0/3/0** | **0/114/0/24/0** |
| B | **8/5/0/3/0** | **60/54/0/14/0** | **1/12/0/3/0** | **0/114/0/14/0** |
| Bw | **3/10/6/0/0** | **27/87/16/0/0** | **0/13/6/0/0** | **0/114/16/0/0** |
| C | **0/13/4/0/0** | 0/114/16/0/0 | **0/13/4/0/0** | 0/114/16/0/0 |
| D | **1/12/4/0/0** | 0/114/16/0/0 | **1/12/4/0/0** | 0/114/16/0/0 |
| D+I (optional) | **1/12/4/0/0** | 0/114/16/0/0 | **1/12/4/0/0** | **0/114/16/0/0** |
| A-fk (ablation) | - | - | **11/2/0/4/0** | **90/24/0/24/0** |
| ORACLE-S (state-probe reference, not a ceiling) | **4/9/0/1/0** | **30/84/0/6/0** | **1/12/0/1/0** | **0/114/0/6/0** |
| ORACLE-O (outcome-oracle reference) | **0/13/1/0/0** | **0/114/6/0/0** | **0/13/1/0/0** | **0/114/6/0/0** |

## horizon_120

H = 120 instead of 60. Options: `horizon=120`.

| policy | c1 core | c1 grid | c2 core | c2 grid |
|---|---|---|---|---|
| A | 12/5/0/0/0 | 90/30/0/0/0 | **1/16/0/0/0** | **0/120/0/0/0** |
| B | 8/9/0/0/0 | 60/60/0/0/0 | **1/16/0/0/0** | **0/120/0/0/0** |
| Bw | 3/14/0/0/0 | 27/93/0/0/0 | **0/17/0/0/0** | **0/120/0/0/0** |
| C | **0/14/3/0/0** | **0/114/7/0/0** | **0/14/3/0/0** | **0/114/7/0/0** |
| D | **1/15/3/0/0** | **0/114/7/0/0** | **1/15/3/0/0** | **0/114/7/0/0** |
| D+I (optional) | **1/15/3/0/0** | **0/114/7/0/0** | **1/16/0/0/0** | **0/120/0/0/0** |
| A-fk (ablation) | - | - | 12/5/0/0/0 | 90/30/0/0/0 |
| ORACLE-S (state-probe reference, not a ceiling) | 4/13/0/0/0 | 30/90/0/0/0 | **1/16/0/0/0** | **0/120/0/0/0** |
| ORACLE-O (outcome-oracle reference) | **0/17/0/0/0** | **0/120/0/0/0** | **0/17/0/0/0** | **0/120/0/0/0** |

## Every change against the baseline row

- status_lists_pending: B c1 core: duplicate 8->5, exactly_once 9->12, unresolved 0->1
- status_lists_pending: B c1 grid: duplicate 60->40, exactly_once 60->80, unresolved 0->3
- status_lists_pending: B c2 core: unresolved 0->1, false_failure 1->0
- status_lists_pending: B c2 grid: unresolved 0->3, false_failure 6->3
- status_lists_pending: Bw c1 core: duplicate 3->2, exactly_once 14->15, unresolved 0->1
- status_lists_pending: Bw c1 grid: duplicate 27->15, exactly_once 93->105, unresolved 0->4
- status_lists_pending: Bw c2 core: unresolved 0->1, false_failure 1->0
- status_lists_pending: Bw c2 grid: unresolved 0->4, false_failure 6->2
- webhooks_not_by_name: A c1 core: duplicate 12->10, exactly_once 5->7
- webhooks_not_by_name: A-fk c2 core: duplicate 12->10, exactly_once 5->7
- bw_without_C15_or_reply_guard: B c1 grid: duplicate 60->70, exactly_once 60->50
- bw_without_C15_or_reply_guard: Bw c1 core: duplicate 3->5, exactly_once 14->12
- bw_without_C15_or_reply_guard: Bw c1 grid: duplicate 27->44, exactly_once 93->76
- tau_5: Bw c1 core: duplicate 3->7, exactly_once 14->10
- tau_5: Bw c1 grid: duplicate 27->40, exactly_once 93->80
- tau_5: Bw c2 core: duplicate 0->1, exactly_once 17->16
- tau_10: Bw c1 core: duplicate 3->4, exactly_once 14->13
- tau_10: Bw c1 grid: duplicate 27->34, exactly_once 93->86
- tau_20: Bw c1 grid: duplicate 27->26, exactly_once 93->94
- tau_20: Bw c2 core: unresolved 0->1, false_failure 1->0
- tau_20: Bw c2 grid: unresolved 0->6, false_failure 6->0
- tau_30: Bw c1 grid: duplicate 27->16, exactly_once 93->104
- tau_30: Bw c2 core: unresolved 0->1, false_failure 1->0
- tau_30: Bw c2 grid: unresolved 0->6, false_failure 6->0
- in_progress_is_wait: A c2 core: unresolved 0->1, false_failure 1->0
- in_progress_is_wait: A c2 grid: unresolved 0->6, false_failure 6->0
- in_progress_is_wait: B c2 core: unresolved 0->1, false_failure 1->0
- in_progress_is_wait: B c2 grid: unresolved 0->6, false_failure 6->0
- in_progress_is_wait: Bw c2 core: unresolved 0->1, false_failure 1->0
- in_progress_is_wait: Bw c2 grid: unresolved 0->6, false_failure 6->0
- abort_record_replays_failure: A c2 core: duplicate 1->0, exactly_once 16->15
- abort_record_replays_failure: B c2 core: duplicate 1->0, exactly_once 16->15
- abort_record_replays_failure: Bw c2 core: exactly_once 17->15
- abort_record_replays_failure: D c2 core: duplicate 1->0, exactly_once 15->14
- abort_record_replays_failure: D+I c2 core: duplicate 1->0, exactly_once 16->15
- abort_record_replays_failure: ORACLE-S c2 core: duplicate 1->0, exactly_once 16->15
- abort_record_replays_failure: ORACLE-O c2 core: exactly_once 17->15
- persistent_faults: A c1 core: duplicate 12->11, exactly_once 5->2, false_failure 0->4
- persistent_faults: A c1 grid: exactly_once 30->24, false_failure 0->24
- persistent_faults: A c2 core: exactly_once 16->12, false_failure 1->3
- persistent_faults: A c2 grid: exactly_once 120->114, false_failure 6->24
- persistent_faults: B c1 core: exactly_once 9->5, false_failure 0->3
- persistent_faults: B c1 grid: exactly_once 60->54, false_failure 0->14
- persistent_faults: B c2 core: exactly_once 16->12, false_failure 1->3
- persistent_faults: B c2 grid: exactly_once 120->114, false_failure 6->14
- persistent_faults: Bw c1 core: exactly_once 14->10, unresolved 0->6
- persistent_faults: Bw c1 grid: exactly_once 93->87, unresolved 0->16
- persistent_faults: Bw c2 core: exactly_once 17->13, unresolved 0->6, false_failure 1->0
- persistent_faults: Bw c2 grid: exactly_once 120->114, unresolved 0->16, false_failure 6->0
- persistent_faults: C c1 core: exactly_once 14->13
- persistent_faults: C c2 core: exactly_once 14->13
- persistent_faults: D c1 core: exactly_once 15->12
- persistent_faults: D c2 core: exactly_once 15->12
- persistent_faults: D+I c1 core: exactly_once 15->12
- persistent_faults: D+I c2 core: exactly_once 16->12, unresolved 1->4
- persistent_faults: D+I c2 grid: exactly_once 120->114, unresolved 6->16
- persistent_faults: A-fk c2 core: duplicate 12->11, exactly_once 5->2, false_failure 0->4
- persistent_faults: A-fk c2 grid: exactly_once 30->24, false_failure 0->24
- persistent_faults: ORACLE-S c1 core: exactly_once 13->9, false_failure 0->1
- persistent_faults: ORACLE-S c1 grid: exactly_once 90->84, false_failure 0->6
- persistent_faults: ORACLE-S c2 core: exactly_once 16->12
- persistent_faults: ORACLE-S c2 grid: exactly_once 120->114
- persistent_faults: ORACLE-O c1 core: exactly_once 17->13
- persistent_faults: ORACLE-O c1 grid: exactly_once 120->114
- persistent_faults: ORACLE-O c2 core: exactly_once 17->13
- persistent_faults: ORACLE-O c2 grid: exactly_once 120->114
- horizon_120: A c2 core: false_failure 1->0
- horizon_120: A c2 grid: false_failure 6->0
- horizon_120: B c2 core: false_failure 1->0
- horizon_120: B c2 grid: false_failure 6->0
- horizon_120: Bw c2 core: false_failure 1->0
- horizon_120: Bw c2 grid: false_failure 6->0
- horizon_120: C c1 core: unresolved 4->3
- horizon_120: C c1 grid: unresolved 16->7
- horizon_120: C c2 core: unresolved 4->3
- horizon_120: C c2 grid: unresolved 16->7
- horizon_120: D c1 core: unresolved 4->3
- horizon_120: D c1 grid: unresolved 16->7
- horizon_120: D c2 core: unresolved 4->3
- horizon_120: D c2 grid: unresolved 16->7
- horizon_120: D+I c1 core: unresolved 4->3
- horizon_120: D+I c1 grid: unresolved 16->7
- horizon_120: D+I c2 core: unresolved 1->0
- horizon_120: D+I c2 grid: unresolved 6->0
- horizon_120: ORACLE-S c2 core: false_failure 1->0
- horizon_120: ORACLE-S c2 grid: false_failure 6->0
- horizon_120: ORACLE-O c1 core: unresolved 1->0
- horizon_120: ORACLE-O c1 grid: unresolved 6->0
- horizon_120: ORACLE-O c2 core: unresolved 1->0
- horizon_120: ORACLE-O c2 grid: unresolved 6->0

## Interpretation (hand-written after the run; notes/sensitivity_conclusions.md, not frozen)

Not written yet.
