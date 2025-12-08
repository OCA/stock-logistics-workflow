This module allows to trace the usage of stock move valuation. That is,
makes it possible to identify which stock moves were used as sources
for a given outgoing stock move, and how much quantity and value was
taken from each source move.

Note: In Odoo 19.0, stock valuation layer model was removed and valuation
is now tracked directly on stock moves through the 'value' field.

This kind of traceability is important in case that at some point you
want to conduct a revaluation (for example, in case that the purchase
order price changes after the products have been received into stock).

Also, it changes the way the outgoing move values are calculated in order to
respect the MTO case. When creating the outgoing move valuation, Odoo uses FIFO
to consume from the first available incoming moves with value. The module stock_move_valuation_usage
improves this process. For standard FIFO, it always uses the oldest
move. However, for MTO cases, when there is a fixed link
between the incoming move and the outgoing move, the system should use the specific 
incoming move not just the oldest one. Also, when the case is not MTO, the system should
avoid using moves that are "reserved".
