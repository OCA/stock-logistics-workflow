.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================
Stock Pack Operation Auto Fill
==============================

For example, if you have an incoming picking with 50 products and you only
receive 49 products, you have to manually set the *Quantity Done* field
on each operation. As the quantity by default is 0 for
each line, you have to write the received quantity on 49 lines.

This module provides a button that let users fill automatically
the *Quantity Done*. Then, the user can just change back
the quantities for the product that hasn't been received yet.

Usage
=====

After confirming the picking, click on the button `Auto fill
operations`. The operations matching the following conditions will be
filled automatically:

* The operation has not be processed (i.e `qty_done == 0`).

* The operation has no package set (i.e `package_id` is empty).

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

To contribute to this module, please visit https://odoo-community.org.
