.. image:: https://img.shields.io/badge/license-LGPLv3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl.html
   :alt: License: LGPL-3

===========================
Stock Account Purchase Line
===========================

This module will add the purchase order line to invoice lines and to account
 move lines. The ultimate goal is to establish the purchase order line as
 one of the key fields to reconcile the Goods Received Not Invoiced accrual
 account.


Usage
=====
The purchase order line will be automatically copied to invoice lines and
account move lines.
* If an invoice is created from a purchase order, the po line is copied
directly to the invoice, and to the account move line upon validation.
* If an invoice is created from a stock picking, the po line is copied from
the stock move to the invoice, and to the account move line upon validation.
* When a stock move is validated and generates an account move, the po line is
copied to the account move line.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/154/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
154/issues/new?body=module:%20
stock_account_purchase_line%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20..
.%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Eficent Business and IT Consulting Services S.L. <contact@eficent.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.