This module integrates `stock_picking_backorder_policy` with sales.

It adds a *Sale Backorder Policy* on the customer, and a *Backorder Policy* on
the sale order, defaulted from the delivery address and adjustable per order.

When the order is confirmed, the policy is carried over to the deliveries it
generates.
