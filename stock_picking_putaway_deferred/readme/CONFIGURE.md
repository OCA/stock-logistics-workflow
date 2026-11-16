On each **Operation Type** that requires deferred putaway:

1. Enable **Allow Putaway Recomputation** (from `stock_picking_putaway_recompute`).
2. Enable **Defer Putaway to Operator**.

With both options active, putaway is skipped at reservation. A "Putaway not
applied" badge appears on the picking form until the operator applies it.
