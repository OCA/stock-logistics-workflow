The module acts on the products whose category uses the **Average Cost (AVCO)**
costing method. Products costed at standard price or FIFO are left untouched.

## Not compatible with automated inventory valuation

Use it only on product categories whose inventory valuation is **manual**.

With automated valuation every valuation layer has a journal entry posted along
with it. This module rewrites the layer when a past mistake is corrected, and it
does not touch that entry, which was posted for the figures the layer used to
hold and may well sit in a period that is already closed. Stock valuation and
accounting would drift apart, silently, by the amount of every correction.

The whole point of restating the past is to reach companies that post the stock
valuation periodically, from the valuation report, rather than movement by
movement. Those that post it automatically already have each correction booked
on the day it was made, which is what Odoo does on its own and what their
accounting expects.

## Valuation by lot/serial number

Both models are supported and can coexist in the same database, so ticking or
unticking **Valuation by Lot/Serial number** on a product needs no special care
from this module's point of view: the layers it already had keep replaying as
the chain they were, and the new ones replay per lot.

Bear in mind that enabling it is Odoo's own operation, not this module's: it
empties the stock out and puts it back, giving **every existing lot the current
average cost of the product**, because the cost each lot was really bought at is
not recorded anywhere before that point. It also refuses to run while any lot
has a negative quantity in a valued location.

## Landed costs and vendor bill price differences

Both add value to a receipt layer without touching its cost, and both read the
remaining quantity to know how much of it is still on hand. They are kept in
step: correcting the cost or the quantity of a layer adjusts its remaining value
by the difference, so what a landed cost or a bill added to it survives the
correction and later corrections are priced right.

Correcting a price on the vendor bill is covered by
`purchase_stock_price_unit_sync`, which applies it to the whole receipt instead
of only to what is still on hand, so that route ends up equivalent to correcting
the receipt or the layer.
