## 18.0.2.0.0 (2026-07-28)

**Support for valuation by lot/serial number.** Odoo keeps one average cost per
product, or one per lot when the product has "Valuation by Lot/Serial number"
ticked, and both kinds of product live in the same database. The module now
replays one valuation chain per lot for the latter and one per product for the
former, so correcting the cost of a lot re-prices what left that lot and leaves
every other lot alone. Until now it averaged over the whole product, which on a
product valuated by lot flattened the real cost of every lot into a single
average.

The layers a product already had before being switched to valuation by lot,
which carry no lot, keep replaying as the single chain they were, so a product
can be switched at any time.

**Fix the cost price of oversold products and lots.** When the accumulated
quantity is zero or negative there are no units left to average against, so the
cost of the incoming move becomes the new average, which is also the cost Odoo's
own negative stock vacuum uses to settle the deficit once enough real stock
arrives. Odoo weighted it against the negative quantity instead, and dividing by
that negative denominator let a receipt lower the average, or even turn it
negative and, from there, make every outgoing move add value to the stock
valuation. The three divisions Odoo leaves unguarded are neutralised:
`product_price_update_before_done`, the tail of `_run_fifo_vacuum` for both the
product and its lots, and `_product_price_update_after_done`.

**Let Odoo's negative stock vacuum run again for average cost products.** It
used to be disabled for every cost method, so nothing corrected the deficit once
real stock arrived.

**The vacuum no longer rewrites the cost of what is in stock.** Odoo closes it
with `standard_price = value_svl / quantity_svl`, and by then `value_svl` carries
the layers it has just written to settle the deficit, which have no quantity:
they correct units that already left the company and say nothing about what the
stock still on hand is worth. On a history that is internally consistent both
figures agree, so nothing changes; on one carrying the damage this module exists
to repair they do not, and the ratio wins over the real purchase price. Seen in
production: a manufacturing order left a product at 6,6567 EUR/unit and the
vacuum immediately rewrote it to 8,3811, which is `1141,67 / 136,220` once three
`Revaluation of ... (negative inventory)` layers had added 210,41 EUR settling
52,18 units delivered a month and a half earlier — the units on hand got 26% more
expensive because of goods that were no longer there. What stands now is the
price derived from the real incoming cost, which is the rule
`_is_avco_spreadable_value` already applies when replaying a chain, so both paths
agree on the cost.

**Quantity corrections keep the remaining quantity in step.** Correcting the
quantity of an already validated move still restates its layer, as it always
did, so a stock valuation asked for a date before the correction comes out right
and the outgoing moves valued in between are re-priced. What was missing is that
the restatement never touched `remaining_qty` and `remaining_value`, the
bookkeeping Odoo needs for the negative stock vacuum and for the vendor bill
price difference, which were left understated by the corrected amount. They are
now kept in step, the correction is applied to the layer of the right lot, and
the vacuum is run afterwards just like Odoo does.

**The remaining value follows a correction.** Correcting the cost or the
quantity of a layer now adjusts its `remaining_value`, which Odoo reads to know
what the units still on hand are worth: the negative stock vacuum prices what it
takes from a layer with it, `stock_landed_costs` accumulates on it and the
vendor bill price difference corrects over it. It was left behind before, so
later deficits were settled at the cost that had just been proven wrong. The
adjustment is a delta, so whatever a landed cost or a bill added to it survives.

**Deficits created by a correction are recorded.** Correcting a receipt below
what had already been delivered leaves the chain short by the difference. That
shortfall is now written as the negative remaining quantity Odoo's negative stock
vacuum looks for, so the next receipt re-prices those units with what was really
paid. It used to be silently dropped, and the stock kept the value of goods that
were never received.

**Value-only layers raise the cost instead of being ignored, and only when they
belong to the stock on hand.** A layer that only carries value and names no
target cost, which is what the stock revaluation wizard writes, is now spread
over the units on hand while replaying, the way a landed cost is. It used to be
skipped, so a later correction left the product with a cost that contradicted
what its own layers were worth.

Not every one of them belongs to that stock, though, and the sign of the layer
it hangs from says which: a child of an incoming layer is a landed cost or a
vendor bill price difference, part of what those units cost, while a child of an
outgoing layer is one of core's negative stock revaluations, settling units that
have already left the company. Spreading the latter over what is still on hand
divided a value by a quantity that had nothing to do with it: a revaluation of
-1120 EUR landing when 0,22 units were held worked out to -5062 EUR/unit, and
from there every later layer in the chain inherited a negative cost. And a
negative average cost is not a low valuation, it is a corruption — it flips the
sign of the value of every layer after it, so outgoing moves start ADDING value
and the product's totals cancel out to something plausible while every single
layer inside is wrong, which is exactly what hides the damage from any report
that reads the totals. So a value-only layer never takes the average below zero,
and the ones settling units already gone no longer touch it at all.

**A server action to force the replay.** *Recompute average cost from here*,
from the stock valuation layers list, replays the chain of the selected layers.
Only the oldest layer of each chain, and of each lot when the product is
valuated by lot, is used: the rest would redo the same work.

**Performance.** The chain is now walked in batches instead of asking for the
next layer one at a time, which was a query per layer, and the dry replay that
works out the starting cost no longer keeps a dictionary per layer only to throw
it away. On a real database, replaying the chain of a product with 68.644 layers
went from not finishing in ten minutes to twelve seconds.

**Removed.** The inventory adjustment branch, which rewrote the quantity and
swapped the locations of the underlying stock move, and the `keep_avco_inventory`
context that drove it. An inventory adjustment layer is simply re-priced with
the running cost, like a return.
