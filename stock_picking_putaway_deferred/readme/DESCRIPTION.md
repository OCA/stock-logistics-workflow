By default, Odoo applies putaway strategies at reservation time (`action_assign`).
This is often too early in contexts where destination slots should only be
committed when the operator is actually performing the transfer (receipts,
putaway-to-shelf workflows, etc.).

This module allows picking types to **defer** putaway calculation: strategies
are not applied at reservation, and the operator must trigger them manually
before starting his work.

Extends `stock_picking_putaway_recompute` — the existing "Recompute Putaways"
button serves as the manual trigger.

.. caution:: This process makes sense only if putaway rules exist.