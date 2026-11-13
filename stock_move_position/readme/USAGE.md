The position is shown on the operations of a transfer, and the batch position
on the operations of a batch transfer, which are listed in that order.

Positions are kept up to date automatically. To renumber them explicitly, use
the action **Renumber positions** on a transfer or a batch transfer (Inventory
managers).

Modules sending positions to a third party can prevent the automatic
renumbering once a record has been sent, by overriding
`_can_auto_renumber_lines()` (see `base_line_numbering`).
