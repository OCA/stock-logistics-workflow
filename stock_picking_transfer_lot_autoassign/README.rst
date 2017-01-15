.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================
Auto-assignment of lots on pickings
===================================

When working with lots, it's very uncomfortable to introduce the quantity,
lot by lot, when transferring pickings from your warehouse (outgoing or
internal).

This module automatically assigns the reserved quantity as the done one, so
that you only have to change it in case of divergence, but having the
possibility of transferring directly.

Configuration
=============

#. Make sure you have selected the proper removal strategy on your product
   categories.
#. Configure the product on the page "Inventory", field "Tracking" with one of
   these values: "By Unique Serial Number" or "By Lots".

Usage
=====

#. Create an outgoing or an internal picking.
#. Include one product with lots and with enough stock.
#. Click on "Mark as Todo" button, and then on "Reserve".
#. Clicking on the icon with the three items bullet list on the "Operations"
   tab you will see that the quantities have been auto-assigned on the "Done"
   column.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/9.0

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@tecnativa.com>

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
