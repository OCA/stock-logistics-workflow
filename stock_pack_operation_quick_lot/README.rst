.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==============================
Stock Pack Operation Quick Lot
==============================

This module allows to set pack operation Lot Name and End of Life Date directly
on picking operations

Configuration
=============

To configure this module, you need to:

#. Activate "Track lots or serial numbers" in Inventory -> Configuration ->
   Setting -> Lots and Serial Numbers
#. Note: the product must have "Tracking | By Lots" in the inventory tab

Usage
=====

To use this module, you need to:

#. Go to Inventory > Operations > All transfers
#. Select a Ready picking or create it and click on Mark as Todo
#. Set Lot Name in Operations tab
#. Set optionally the end of life date in the proper column
#. When the picking will be transferred, the lot will be created with that
   name and date.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/9.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* `Tecnativa <https://www.tecnativa.com>`_:
  * Carlos Dauden

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
