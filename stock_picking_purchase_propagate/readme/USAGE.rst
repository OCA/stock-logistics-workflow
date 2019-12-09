This module can help you if your warehouse uses two- or three- steps reception.

In such a case, odoo's scheduler will generate internal transfers pickings with
the procurement group defined on each orderpoint of the products in need.

So, if no procurement group is defined on the orderpoints, Odoo will generate
only one internal transfer picking for all the products having needs, even if
suppliers and delays could be totally different.

If the product is to be purchased, the scheduler will also generate a purchase
order. However when confirming this purchase order, the generated receipt
picking and its move will get the procurement group from the sale order, which
doesn't match the procurement group of the ensuing internal transfers, what
could be baffling for the stock operator who has to find the ensuing internal
transfer.

Moreover, if the quantity is changed before confirming the purchase order, the
receipt picking will be generated with the PO's quantity, whereas the ensuing
moves and picking will still have the original quantity from the orderpoint.
Therefore, if the quantity was reduced on the purchase order, the stock
operator won't be able to close the move line in waiting state, although it's
not expected to receive more quantity until the next purchase order.

Instead of provoking such headaches to stock operators, this module will
propagate the procurement group and the quantity of the purchase order to the
whole chain of moves and reassign them to new pickings.

This allows to have a clear match through the procurement group between
purchase order, receipts and internal transfers, and allows as well stock
operators not to worry about missing quantities which weren't ordered in the
first place.
