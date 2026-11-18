This module allows to trace the usage of stock move valuation. That is,
makes it possible to identify which stock moves were used as sources
for a given outgoing stock move, and how much quantity and value was
taken from each source move.

Note: In Odoo 19.0, stock valuation layer model was removed and valuation
is now tracked directly on stock moves through the 'value' field.

Note: In Odoo 20.0, the value of the outgoing FIFO moves is replayed when
an earlier move changes (date, quantity or cost), or when a receipt fills
stock that was already delivered. The usage records of the replayed moves
are rebuilt from that replay, so a receipt that fills a negative stock is
linked to the deliveries it covers, for the quantity it covers.

This kind of traceability is important in case that at some point you
want to conduct a revaluation (for example, in case that the purchase
order price changes after the products have been received into stock).
