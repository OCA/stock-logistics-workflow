.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Product Expiry Simple
=====================

This module is similar to the official `product_expiry <https://www.odoo.com/apps/modules/10.0/product_expiry/>`_ module that adds support for *Expiry Dates* on products, but it is both simpler and better:

* Only one *Expiry Date* field instead of 4 fields (End of Life Date, Best before Date, Removal Date, Alert Date)!
* Use date field instead of datetime field for *Expiry Date*
* No automatic computing of Expiry Date based on a delay configured on product because it is not used most of the time (for manufacturing companies, the rules that control expiry dates are usually more complex than that ; for reseller companies, they have to copy the expiry date written on the good when they receive it in their warehouse)
* List views of production lots and quants have a color depending on expiry date: green if expiry date is in the future, red if it is in the past.
* Ability to show stats about expiry dates on quants pivot table (because, with this module, the *Expiry Date* is a related stored field on stock.quant).

This modules keeps the main feature of the official *product_expiry* module: the support of FEFO (First Expiry First Out).

I decided to develop this module because, after implementing *product_expiry* at several companies, I noticed that I spent more time inheriting the official *product_expiry* module to make always the same kind of changes that re-developping a simpler and better alternative.

Configuration
=============

No configuration needed.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

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
