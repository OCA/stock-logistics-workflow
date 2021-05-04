This module allows to trace the usage of stock valuation layer. That is,
makes it possible to identify in what stock moves was a given valuation layer
used, and how much quantity was taken by the particular stock move.

This kind of traceability is important in case that at some point you want
to conduct an revaluation (for example, in case that the purchase order price
changes after the products have been received into stock).

Also, it changes the way the outgoing layers are created in order to respect
the MTO case. When creating the out svl, Odoo takes the first layer available
with value. The module stock_valuation_layer_usage arises an issue with that
Odoo process. Odoo will take always the oldest svl. However, that is not the
case for MTO. When there is a fixed link between the incoming move and the
outgoing move, at the time of creating the outgoing svl the system should
take the specific incoming svl not just the oldest one. Also, when the case
is not MTO, the system should avoid using svl that are "reserved".
