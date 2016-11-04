.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

=============
Stock deposit
=============

This module extends standard WMS to manage customers deposit locations by
warehouse.
Deposited stocks can't be selected in regular delivery orders unless you have
been returned it.
Deposited stocks have been evaluated in inventory valuation.

Installation
============

The installation module process create a deposit location per warehouse and
two picking types, one for outgoing deposits and other for returned deposits.

Configuration
=============

To configure this module, you need to:

#. Go to *Inventory > Settings > Product Owners* and click
   "**Manage consignee stocks (advanced)**".

Usage
=====

To use this module, you need to:

#. Go to products and create one of type "Stockable".
#. Update quantities on hand to have stock of it.
#. Go to inventory dashboard and click on "Deposit out" card to do a new
   transfer.
#. Create a picking with owner and select the product to do the transfer.

To track current deposits:

#. After that process, you can view deposit quantities in product form view.
#. You can also see the deposits for all your products in the menu entry
   Inventory --> Reports --> Deposited location inventory.

For regularizing deposited quantities (this means to deliver deposited stock
to the customer as a normal outgoing move.), you need:

#. Go to Inventory --> Reports --> Deposited location inventory, select quants
   that you want to regularize and click on more actions and select
   "**Regularize deposit quants**". This process creates delivery orders from
   deposit location to customer location.

To give back deposit to you warehouse, you need:

#. Just make standard process, go to deposit picking and click in buton
   "Reverse".

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/9.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/154/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/
  blob/master/template/module/static/description/icon.svg>`_.
* https://openclipart.org/detail/168751/saving-up
* https://openclipart.org/detail/171740/wooden-package


Contributors
------------

* Sergio Teruel <sergio.teruel@tecnativa.com>

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
