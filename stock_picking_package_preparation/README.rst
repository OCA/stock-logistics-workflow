.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Stock Picking Package Preparation
=================================

This module adds a new document in the Warehouse menu: **Package
Preparation**. It works on a selection of pickings and allows to add
them all in the same package, then to transfer all the pickings at once.

A possible use case is to put all the selected pickings on a pallet.

Installation
============

 * This module depends only on the **stock** module.

Configuration
=============

 * No special setup

Usage
=====

To use this module, you need to:

 * Go to Warehouse > Package Preparation

From there, you can create a new preparation.
Choose a partner then the selection of pickings you want in the package.
You can choose a logistic unit or a packaging, they will be set on the
generated package.

When you click on **Put in pack**, it generates the pack, which is not
finalized yet (no quants), but you can verify the operations in the
**Operations** tab.
Eventually, when you click on **Done**, all the pickings will be
transfered and the package operations will be performed.

Known issues / Roadmap
======================

 * No printed document for the preparation


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/stock-logistics-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/stock-logistics-workflow/issues/new?body=module:%20stock_picking_package_preparation%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Lorenzo Battistini <lorenzo.battistini@agilebg.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
