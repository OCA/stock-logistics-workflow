.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

================================
Stock Picking Purchase Propagate
================================

This module allows to propagate the procurement group and the quantity of the
purchase order at its confirmation to the ensuing picking and stock moves and
their destination moves and pickings.

Usage
=====

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

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock_logistics_workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Vincent Renaville <vincent.renaville@camptocamp.com>
* Akim Juillerat <akim.juillerat@camptocamp.com>

Do not contact contributors directly about support or help with technical issues.

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
