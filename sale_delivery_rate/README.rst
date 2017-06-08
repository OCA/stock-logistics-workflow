.. image:: https://img.shields.io/badge/license-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Sale Delivery Rates
===================

This module extends the notion of delivery rate quotes introduced in 
``stock_picking_rate`` to sale orders. The new quote type is compatible with the 
``Set price`` button used on sale orders to calculate a delivery price. Also, 
when a sale order with such rate quotes is confirmed and results in the 
creation of a stock picking, the picking will be updated with equivalent stock 
picking delivery quotes.

Installation
============

To install this module, simply follow the standard install process.

Configuration
=============

No configuration is needed or possible.

Usage
=====

Install and enjoy.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/9.0

Known Issues / Roadmap
======================

* This module expects each sale order to result in a single picking when 
  confirmed and may produce incorrect results if multiple pickings are created

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/stock-logistics-workflow/issues>`_.
In case of trouble, please check there if your issue has already been 
reported. If you spotted it first, help us smash it by providing detailed and 
welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Oleg Bulkin <obulkin@laslabs.com>

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
