.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Product Unique Serial Number
============================

Allow to control product serial lot number with a unique relation, adding a restriction
to avoid stock moves with quantity different than 1, only if **Unique Lot** option (explained later)
is enabled

Installation
============

To install this module, just selected from available modules.

Configuration
=============

To configure serial uniqueness feature, do the following

* Go to Warehouse > Products > Products

* Choose the product you need to acomplish unique serial

* Get into Inventory tab in the form view and enable at least one of the
  lots available options for serial lot tracking, and then **Unique Lot** option
  will appear to enable it

Usage
=====
When doing a warehouse transfer, there are two posibilities for serial lot number treatment :

#. Incoming transfer: Serial numbers will not appear unless it have not already a
   stock move related and letting to the user create a new one from scratch

#. Outgoing / Internal transfer: Dont show unused serial lots leaving to the user
   to select only those one that have associated moves


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/8.0

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================

* When computing last location for a lot based on quants, it fails, this is not
  fully tested
* Look how to append domain strings

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/
stock-logistics-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/
stock-logistics-workflow/issues/new?body=module:%20
product_unique_serial%0Aversion:%20
8.0.1.0.1%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Moisés Lopez <moylop260@vauxoo.com>
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
