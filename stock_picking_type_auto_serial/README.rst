.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Automatic Serial Generation
===========================

This module adds the possibility to generate serials automatically for products
with tracking set to serial.

Installation
============

To install this module, you need to:

* Click on install button

Configuration
=============

To configure this module, you need to:

* Set the flag 'Automatic Serial Generation' to True on the picking operation.
  Note that the picking operation should be of type 'Supplier'.
* Set the tracking on the product to track 'By Unique Serial Number', and set
  the flag 'Automatic Serial Generation' to True.
* Create a picking with the configured picking operation and configured
  product.
* Add a Quantity to process or click directly on 'Validate' button.
* As result: serials are generated depending the selected quantity.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/9.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Zakaria Makrelouf (ACSONE SA/NV) <z.makrelouf@gmail.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
