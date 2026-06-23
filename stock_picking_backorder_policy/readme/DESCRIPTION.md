When a transfer is only partially done, Odoo decides whether to create a
backorder for the remaining quantity based on the **backorder policy of the
operation type** (Ask, Always or Never).

That default fits the warehouse, but the right answer is often driven by the
*customer* instead: some customers always want the rest shipped later, others
never do.

This module lets you **optionally override** that operation type default, on
the partner and on the transfer itself:

- **Ask**: the user is prompted (standard behaviour).
- **Always**: a backorder is created automatically for the remaining quantity.
- **Never**: the remaining quantity is cancelled and no backorder is created.

The policy is shared by a company and its contacts (delivery addresses). A
transfer created for a partner (for instance directly from the Inventory app)
defaults to that partner's policy, and the value can still be adjusted on the
transfer. When left empty, the operation type's own policy applies, exactly
like standard Odoo.
