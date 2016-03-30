.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Block Serial Numbers/lots
=========================

This module allows you to define whether a Serial Number/lot is blocked
or not.
The default value can be set on the Product Category, in the
field "Block new Serial Numbers/lots".

Configuration
=============

To allow a user to block or unblock a Lot:

#. open the user settings (menu "Configuration > Users")
#. in the "Warehouse" section, check the box
   "Can block/unblock Serial Numbers/Lots"

Usage
=====

Two new buttons let you block/unblock a Serial Number/lot in the form view.
Blocking/unblocking can also be done from the list view, by selecting the
Serial Numbers/lots and choosing the option "Block/Unblock lots".

Only lots which have no reservation can be blocked.

Delivery Orders are not allowed to select a blocked Serial Number/lot.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/stock-logistics-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/stock-logistics-workflow/issues/new?body=module:%20stock_lock_lot%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <anajuaristi@avanzosc.es>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Lionel Sausin <ls@numerigraphe.com>

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
