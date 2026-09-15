Go to *Inventory > Reporting > Lot Valuation Allocation*.

The list is grouped by lot/serial number and ordered by actual date. Each line
drills through to the valuation layer it comes from, and the group total equals
the lot's remaining value. The pivot view breaks the allocated amount down by
lot and period.

Historical layers
~~~~~~~~~~~~~~~~~

On installation, a scheduled action backfills the valuation layers that already
exist. It processes them in batches, oldest first, and deactivates itself once
the backlog is drained. Progress is kept in the
``stock_valuation_fifo_lot_allocation.backfill_last_id`` system parameter; to
rebuild the ledger from scratch, delete the allocation records, reset that
parameter and the ``...backfill_balanced`` one, and reactivate the scheduled
action (or run the *Run Lot Allocation Backfill* server action).

Historical figures cannot be reconstructed exactly: remaining quantities are a
current snapshot rather than an as-of-date value, and past per-lot FIFO
consumption is not recorded per layer. Incoming layers are backfilled exactly;
outgoing and value-only layers are approximated, and once the backlog is
drained a single *Opening allocation adjustment* record per lot absorbs the
difference, so the invariant holds exactly and every approximation stays
visible in one auditable row.

Forced FIFO lots
~~~~~~~~~~~~~~~~

When a *Force FIFO Lot/Serial* is set on an outgoing move line, the ledger
charges the lot whose FIFO balance was consumed, not the lot physically
shipped. This is what keeps the ledger consistent with the valuation.
