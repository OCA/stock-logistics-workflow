.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
Product Serial
==============

This module improves the usability of serial numbers in Odoo. It is very usefull when you purchase and/or sell products with one serial number per item.

Configuration
=============

This module adds a new selection field *Lot Split Type* on the product form
under the *Inventory* tab ; you should set it to *Single* on products that have
one serial number per item.

Usage
=====

On the transfer wizard, for the products with *Lot Split Type* = *Single*, you will automatically get one line per unit (i.e. if the stock move has qty = 3, you will get 3 lines with qty = 1).

This module also adds a button *Spread Serial Numbers* on the transfer wizard which make it easy to create a sequence of serial numbers or import serial numbers from a file.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/8.0

For further information, please visit:

 * https://www.odoo.com/forum/help-1

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/stock-logistics-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/stock-logistics-workflow/issues/new?body=module:%20product_serial%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
