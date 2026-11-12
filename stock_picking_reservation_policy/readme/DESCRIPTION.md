By default, Odoo reserves whatever quantity is available for a transfer's lines
(stock moves), leaving the rest as *partially available*.

This module adds a **Reservation Policy** that controls this behavior, on the
operation type and on the transfer itself:

- **Partial**: reserve whatever quantity is available (standard behavior).
- **All or nothing per line**: each transfer line (stock move) is reserved only
  if its **full** quantity can be reserved from stock; otherwise that line stays
  entirely unreserved.

The all-or-nothing rule is applied **per line (stock.move)**, independently for
each line of the transfer — not on the transfer as a whole. One line may be fully
reserved while another, short on stock, stays unreserved.

The transfer defaults its policy from the operation type, and the value can be
adjusted on the transfer.

It is similar in spirit to the *Shipping Policy* (`move_type`), but it applies at
**reservation** time on each line, rather than at delivery time. It only affects
reservation from stock: lines fed by chained (origin) moves keep their standard
behavior.
