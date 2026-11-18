When a transfer is only partially done, Odoo decides whether to create a
backorder for the remaining quantity based on the **backorder policy of the
operation type** (Ask, Always or Never).

That default fits the warehouse, but the right answer is often driven by the
document the transfer comes from: some customers always want the rest shipped
later, others never do.

This module lets you **optionally override** that operation type default on
the transfer itself:

- **Ask**: the user is prompted (standard behaviour).
- **Always**: a backorder is created automatically for the remaining quantity.
- **Never**: the remaining quantity is cancelled and no backorder is created.

When left empty, the operation type's own policy applies, exactly like
standard Odoo.

The policy is carried by the operations, so it survives multi-step routes and
make-to-order chains. Modules building on top of this one seed it from their
own documents: `sale_stock_picking_backorder_policy` for deliveries generated
from a sale order, `purchase_stock_picking_backorder_policy` for receipts
generated from a purchase order.
