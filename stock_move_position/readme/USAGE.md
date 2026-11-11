The position is shown on the operations of a transfer.

Positions are kept up to date automatically. To renumber them explicitly, use
the action **Renumber positions** on a transfer (Inventory managers).

Modules sending positions to a third party can prevent the automatic
renumbering once a record has been sent, by overriding
`_line_renumber_needed()` (see `base_line_numbering`).
