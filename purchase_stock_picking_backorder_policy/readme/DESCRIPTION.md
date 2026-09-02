This module integrates `stock_picking_backorder_policy` with purchases.

It adds a *Purchase Backorder Policy* on the vendor, and a *Backorder Policy*
on the purchase order, defaulted from the vendor and adjustable per order.

When the order is confirmed, the policy is carried over to the receipt it
generates.
