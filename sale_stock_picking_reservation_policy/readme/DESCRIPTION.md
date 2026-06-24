This module integrates `stock_picking_reservation_policy` with sales.

It adds a *Reservation Policy* on the sale order, defaulted from the customer
(or delivery address) and adjustable per order.

When the order is confirmed, the policy is carried over to the deliveries it
generates. With an *All or nothing per line* order, each delivery line (stock
move) is reserved only if its **full** quantity can be reserved from stock;
otherwise that line stays unreserved. The all-or-nothing rule is applied **per
line (stock.move)**, independently for each line, not on the delivery as a whole.
