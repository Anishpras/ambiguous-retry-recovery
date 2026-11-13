Written by the implementer after the v1.0 collection run. This file is interpretation, not code or fixtures, so it is not frozen; `run_sim.py` copies it into `results/predictions_check.md`.

**U09a: D+I duplicates in S15 under contract 2. Cause: a prediction error, not an implementation bug.**

- **The prediction.** The design-update prediction lists the contract-2 duplicates as "only in S15 (A, B, D and ORACLE-S)". It does not mention D+I.
- **Why D+I behaves like D here.** D+I is D plus one idempotent resend, so it inherits D's retry rule. In S15, the `aborted` webhook for a1 arrives at t = 4. It is an authoritative terminal negative, and it covers the only dispatched attempt. D's rule therefore dispatches a2 at t = 4, under D+I exactly as under D.
- **Why that retry executes.** a1's abort at t = 3 released the contract-2 dedup record. a2 therefore executes and commits at t = 6.
- **Where the duplicate comes from.** The provider then violates its guarantee and commits a1 at t = 12, giving two effects. The duplicate is contract-caused (a2 was a justified retry), and D+I records the conflict for a1 when the `committed` webhook arrives at t = 14.
- **Why D+I's own resend is not involved.** D+I's resend fires at t = 6, on the first status reply after the t = 5 timeout. That reply's replica was cut off at t = 4, so it shows only a1 as terminal; a2 is still in flight and the operation is unresolved. The resend a3 is answered with a replay of a2's effect, so it adds no effect.
- **Conclusion.** Both D and D+I duplicate in S15 for the same reason. The trace is in `results/traces/contract2/D+I/S15.jsonl`; `python3 run_sim.py --show 2 D+I S15` prints it.
- **Disclosure.** The implementer noticed this omission by hand while applying the design update, before the freeze. As instructed, the prediction was not adjusted.

Every other prediction matches. Three of the matches depend on implementation clarifications:

- **U04b and T01 (Bw).** These rely on clarification C15: Bw issues no status read when the belief is already `complete` at the end of its wait. In S15, Bw becomes `complete` at t = 14 and its wait (started at t = 4) ends at t = 19, so no read is issued at all. The prediction text "before its read" assumed a read would follow. That detail differs from the expectation, but the predicted outcome (exactly once, `complete` at t = 14) holds.
- **P06, P16 and P17 (A and B).** These rely on clarification C9, the literal reading of A and B: failure signals are acted on whatever the current belief.
  - In the core matrix this reading changes no outcome. A scan of the traces finds no timeout, `error`, `in_progress`, `rejected` or `not_found` reaching A, B or Bw while their belief is `complete`.
  - A's two dispatches after completion (S06 at t = 30, S14 at t = 12) are triggered by failure-named webhooks. Those retries are behaviour that §3 specifies ("last terminal-looking event wins"), not a consequence of C9.
  - The reading did matter in the v1.0 grids: under contract 1, 24 of A's and 26 of B's grid duplicates followed a retry made after a webhook had already confirmed completion.
  - Revisions v1.1 and v1.1.1 (study lead) make A, B and Bw ignore request-path failure signals, including replies to their own status reads, once `complete`; see PROTOCOL.md Revisions and `results/revision_v1.1_delta.md`. The predictions named above do not depend on these revisions.
