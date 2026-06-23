On a sale order, the *Backorder Policy* is set by default from the customer (or
delivery address) and can be adjusted manually before confirmation.

When the order is confirmed, the policy is carried over to the deliveries it
generates, including multi-step routes. On validation of a partial delivery:

- **Ask**: the usual backorder prompt is shown.
- **Always**: a backorder is created automatically.
- **Never**: the remaining quantity is cancelled.

The customer's policy is configured on the contact form (see
*stock_picking_backorder_policy*).
