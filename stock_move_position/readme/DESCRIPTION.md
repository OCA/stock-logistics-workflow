Adds a stable line reference on stock moves, numbered 1, 2, 3, ...: the
**position** of the move in its transfer.

Positions are renumbered automatically when moves are added to or removed
from a transfer. A split move keeps the position of the original one.
The moves sorted by position follow the numbers (10 after 9).

The numbering comes from `base_line_numbering`. The position of the moves in
their batch transfer is added by `stock_picking_batch_move_position`.
