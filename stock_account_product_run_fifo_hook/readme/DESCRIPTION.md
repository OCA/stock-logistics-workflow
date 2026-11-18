This module adds hook points in the FIFO valuation process to add more flexibility
in the information that is stored and processed during FIFO candidate calculations.

In Odoo 19, the valuation logic has shifted from `stock.valuation.layer` to `stock.move`.
This module provides extension points for custom modules to:

- Access FIFO candidate move information during valuation
- Know which outgoing move consumes each FIFO candidate

In Odoo 20, the per-quantity FIFO computation moved from `_run_fifo()` to
`_get_fifo_value()` (`_run_fifo()` now values whole products in batch), so the hook
is injected in `_get_fifo_value()`. Core no longer passes the outgoing move being
valued, so this module also patches `stock.move._set_value()` to put it in the
`valued_move` context key.

Odoo 20 also replays the FIFO valuation (`_run_fifo(correction=True)`) when a valued
move line quantity, location or lot is edited, a move date changes, a product value is
adjusted, the costing method changes, or a receipt fills stock that was already sold.
This module patches it to call the same hook for each candidate consumed during the
replay, and adds `_run_fifo_correction_reset()` before it so that custom modules can
drop the data stored for the outgoing moves that are replayed.
