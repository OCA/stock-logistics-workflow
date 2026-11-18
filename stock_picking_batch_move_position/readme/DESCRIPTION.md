Adds the **batch position** on stock moves: the position of the move in its
batch transfer, numbered 1, 2, 3, ... The moves of a transfer stay together,
and the transfers follow their order in the batch.

Batch positions are renumbered automatically when moves are added to or
removed from the transfers of a batch, and when transfers are added to a
batch or reordered in it. A transfer added to a batch goes after the
transfers already in it, so the existing batch positions don't move. A split
move keeps the batch position of the original one. The moves sorted by
batch position follow the numbers (10 after 9).

The position of the moves in their transfer comes from `stock_move_position`.
