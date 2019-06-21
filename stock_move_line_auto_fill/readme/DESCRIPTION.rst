This module alows to auto fill quantities in picking operations and autoassignment
lots quantities.

In Odoo, if you schedule to transfer 50 products and only receive 49, you have
to change the quantity directly on the picking.
As the quantity by default is 0 for each line, you have to write the received
quantity on 49 lines.

In this module we have added a button that helps users to fill automatically
the scheduled quantities. Then, the user can just change back the quantities
for the product that hasn't been received yet.

Products with lots
==================
When working with lots, it's very uncomfortable to introduce the quantity,
lot by lot, when transferring pickings from your warehouse (outgoing or
internal).

This module automatically assigns the reserved quantity as the done one, so
that you only have to change it in case of divergence, but having the
possibility of transferring directly.
