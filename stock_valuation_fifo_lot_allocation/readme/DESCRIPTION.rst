For FIFO products tracked by lot/serial number, this module persists one record
every time a stock valuation layer is created, capturing how much of that
layer's value is charged to each lot.

``stock_valuation_fifo_lot`` already produces the correct per-lot remaining
value on the stock move line, but it only exposes the current balance. Landed
costs, vendor bill price differences and revaluations leave no per-lot trace, so
there is no way to explain how a lot arrived at its value. This module records
the split at the moment the layer is created, while the information needed to
split it is still available, so that at audit time you can list, group and drill
down into exactly why each lot carries the value it does.

The ledger satisfies the following invariant, per lot::

    sum(allocated_amount) == sum(stock.move.line.value_remaining)
