.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
Stock Check No Negative
=======================

This module extends warehouse functionalities to not reach below zero in product available quantities

Installation
============

Just select it from available modules to install it, there is no need to extra installations

Configuration
=============

This module brings product configurations per products as the following,

* Go to Products > Products, in the Inventory tab is now allowed to select an option
  called "**Check no negative**" to activate this module main functionality

Usage
=====

* Before doing a transfer this will check availability for every single product (with the option mentioned before marked) within the transfer

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/8.0

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================

* TODO in method check_before_action_done: stock_move use product_uom

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/
stock-logistics-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/
stock-logistics-workflow/issues/new?body=module:%20
stock_no_negative%0Aversion:%20
8.0.1.0.10A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Moises Lopez <moylop260@vauxoo.com>
* Osval Reyes <osval@vauxoo.com>

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
