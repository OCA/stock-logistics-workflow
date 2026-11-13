Adds two stable line references on stock moves, numbered 10, 20, 30, ...:

- **Position**: the position of the move in its transfer.
- **Batch position**: the position of the move in its batch transfer. The
  moves of a transfer stay together, and the transfers follow their order in
  the batch.

Positions are renumbered automatically when moves are added to or removed
from a transfer or a batch, and when transfers are added to a batch or
reordered in it. A transfer added to a batch goes after the transfers already
in it, so the existing batch positions don't move. A split move keeps the
positions of the original one.

The numbering comes from `base_line_numbering`.
