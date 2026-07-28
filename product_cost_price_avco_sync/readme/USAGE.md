## Correcting a mistake

There are four ways of correcting a purchase, and all of them end up in the same
place: the layer is restated as if it had always held the corrected figures, the
outgoing moves valued in between are re-priced, and the cost of the product, or
of the lot, follows.

| What you correct | Where | What it takes |
|---|---|---|
| The **cost** of a receipt | The `unit_cost` of its valuation layer | This module |
| The **quantity** of a done move, incoming or outgoing | The quantity of the move line | This module |
| The **price** of a purchase order already received | The order line | `purchase_stock_price_unit_sync` |
| The **price** on the vendor bill | The invoice line | `purchase_stock_price_unit_sync` |

Correcting the same price twice, on the order and then on the bill, does not
count it twice: the second one finds the layer already worth what it says and
does nothing.

## Forcing it by hand

For the times a correction could not run on its own, such as layers written
while this module was not installed, the **Recompute average cost from here**
action is available from the Action menu of the stock valuation layers list.
Select one or more layers and the chain is replayed from each of them.

Only the oldest layer of each chain in the selection is used, because replaying
corrects everything that comes after the starting point and the rest would redo
the same work. On a product valuated by lot each lot is a chain of its own, so
the oldest layer of each lot is kept.

Replaying a long chain rewrites every layer after the starting point, in a
single transaction. On a product with hundreds of thousands of layers, start as
late in the chain as the correction allows.

## What happens with everything else

These flows need nothing from you and are not disturbed by a correction:

- **Landed costs**, applied before or after the correction, and split per lot.
  What they added to the layer is not purchase cost, so it survives untouched
  and the correction only moves the cost of the goods.
- **The stock revaluation wizard**. What it adds is spread over the units on
  hand, the same way a landed cost is, so the cost of the product keeps matching
  what its layers are worth.
- **Negative stock.** With no units left to average against, a receipt sets the
  cost to the price actually paid, and Odoo's own vacuum settles the outstanding
  deficit with that same price once enough real stock arrives. Correcting a
  receipt down below what had already been delivered records the shortfall as
  the deficit the vacuum looks for, so those units get re-priced too.

  That shortfall is recorded on the **last** outgoing move of the chain, which
  is where it would have fallen short in chronological order, rather than on
  whichever delivery took each particular unit. Reconstructing that would mean
  replaying the consumption backwards, and it would change nothing: an average
  cost is spread over the whole quantity, so what matters is that the deficit
  exists and is settled, not which delivery it is attached to.
- **Inventory adjustments** and **returns** are valued at the cost of the moment
  rather than averaged in, and a correction re-prices them along with the rest.
- **Switching a product to or from valuation by lot**, at any time. The layers it
  already had keep replaying as the single chain they were.

## What is left to Odoo

- **Vendor bill refunds**, which Odoo compensates against the original bill with
  a logic of its own.
- **Layers created straight from code**, outside a stock move and without
  running Odoo's negative stock vacuum, as a third party module could do. They
  do not trigger anything: use the server action above if a chain ever needs it.
- Products that are not average costed, and automated inventory valuation, which
  is not compatible at all. See the configuration notes.
