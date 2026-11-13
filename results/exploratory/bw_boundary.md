# Where Bw duplicates: unit-step boundary

_Exploratory, post-review (v1.2). Not pre-specified; the frozen v1.1.1 core tables remain the record._

Contract 1, policy Bw, timeout T = 5. Grid 1: a1 commits at t = 2 with its response lost; the `committed` receipt arrives at t = R (3 to 70, or lost); status lag L = 0 to 64. A duplicate needs both the receipt to miss the verify window and the verify read to miss the commit.

| tau | duplicates | smallest L with a duplicate | smallest R with a duplicate | rectangle {L >= L*, R >= R* or lost} exact? | predicted L* = tau + T - c + 1 | predicted R* = tau + T + 2 |
|---|---|---|---|---|---|---|
| 5 | 3360 of 4485 | 9 | 12 | yes | 9 | 12 |
| 10 | 2805 of 4485 | 14 | 17 | yes | 14 | 17 |
| 15 | 2300 of 4485 | 19 | 22 | yes | 19 | 22 |
| 20 | 1845 of 4485 | 24 | 27 | yes | 24 | 27 |
| 30 | 1085 of 4485 | 34 | 37 | yes | 34 | 37 |

Map for tau = 15 (rows L = 0..64, columns R = 3..70 then `L` = lost; `X` = duplicate, `.` = one effect):

```
L\R  34567890123456789012345678901234567890123456789012345678901234567890L
  0  .....................................................................
  1  .....................................................................
  2  .....................................................................
  3  .....................................................................
  4  .....................................................................
  5  .....................................................................
  6  .....................................................................
  7  .....................................................................
  8  .....................................................................
  9  .....................................................................
 10  .....................................................................
 11  .....................................................................
 12  .....................................................................
 13  .....................................................................
 14  .....................................................................
 15  .....................................................................
 16  .....................................................................
 17  .....................................................................
 18  .....................................................................
 19  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 20  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 21  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 22  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 23  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 24  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 25  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 26  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 27  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 28  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 29  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 30  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 31  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 32  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 33  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 34  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 35  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 36  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 37  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 38  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 39  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 40  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 41  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 42  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 43  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 44  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 45  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 46  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 47  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 48  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 49  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 50  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 51  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 52  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 53  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 54  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 55  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 56  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 57  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 58  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 59  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 60  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 61  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 62  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 63  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 64  ...................XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Grid 2 (tau = 15, receipt lost, response lost): a1 commits at t = 1 + E. Predicted: duplicate iff the verify read at t = T + tau = 20 cannot see the commit, i.e. 1 + E > 20 - L, i.e. E + L >= 20 (while the commit falls before F).

Result: 1450 of 1640 cells duplicate; cells disagreeing with `E + L >= 20`: none.

General condition (lost ack or pending, no receipt in time): Bw is duplicate-free iff its verify read sees the commit, i.e. commit_time <= t_signal + tau - L. With commit_time <= dispatch + E_max (an in-flight bound covering arrival and execution) and t_signal = dispatch + T, a sufficient condition is **tau >= E_max + L_max - T**. Both grids above confirm it at unit resolution.
