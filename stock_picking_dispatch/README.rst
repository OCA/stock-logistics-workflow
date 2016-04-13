.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Picking dispatch
================

This module allows you to group various pickings into a dispatch order (picking wave),
having all the related moves in it and assigned to a warehouse keeper.

Wave picking is an application of short interval scheduling, to assign orders
into groupings (waves) and release them together so as to allow management to
coordinate the several parallel and sequential activities required to complete
the work.

The individual orders in the wave are dependent on the criteria used to make
the selection. To organize the sequence of orders and assignment to waves,
consistent with routing, loading and planned departure times of shipping
vehicles or production requirements, etc., to reduce the space required for
shipping dock handling to assemble orders and load; and To assign staff to
each wave and function within a wave, with the expectation that all the work
assigned to each wave will be completed within the wave period.

From there, you can perform various operations:

 * Check availability of related moves and pickings
 * Organize your deliveries by grouping on interesting matter (e.g. by transporter, by type of goods, etc..)
 * Make partial delivery
 * Print a report to pick the proper goods at once

Known issues / Roadmap
======================

Unported features
-----------------
Until V7, when marking a picking dispatch as done, it was possible to choose partial quantities for each move and create backorder picking dispatch.
This feature is currently unported in V8 / V9.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/stock-logistics-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/stock-logistics-workflow/issues/new?body=module:%20picking_dispatch%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Peter Langenberg <peter.langenberg@bubbles-it.be>
* Rudolf Schnapka <rs@techno-flex.de>
* Matthieu Dietrich <matthieu.dietrich@camptocamp.com>
* Romain Deheele <romain.deheele@camptocamp.com>
* Leonardo Pistone <leonardo.pistone@camptocamp.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Joël Grand-Guillaume <joel.grandguillaume@camptocamp.com>
* Cyril Gaudin <cyril.gaudin@camptocamp.com>


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

