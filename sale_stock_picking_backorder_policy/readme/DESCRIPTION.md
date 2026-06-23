This module integrates `stock_picking_backorder_policy` with sales.

It adds a *Backorder Policy* on the sale order, defaulted from the customer
and adjustable per order.

When the order is confirmed, the policy is carried over to the deliveries it
generates.
