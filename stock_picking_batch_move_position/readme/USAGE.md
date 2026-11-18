The batch position is shown on the operations of a batch transfer, which are
listed in that order.

Batch positions are kept up to date automatically. To renumber them
explicitly, use the action **Renumber positions** on a batch transfer
(Inventory managers).

Modules sending batches to a third party can prevent the automatic
renumbering once a batch has been sent, by overriding
`_line_renumber_needed()` (see `base_line_numbering`).
