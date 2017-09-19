.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Automatic Move Processing
=========================

This module adds the possibility to have move automatically processed as soon
as the products are available in the move source location.

It also adds the possibility to define the move as being automatic in
a procurement rule.

Automatic moves are triggered by previous move when the move is chained
or by the scheduler otherwise.

Note that automatic moves are given a procurement group name "Automatic",
whatever the user or the procurement rule selects.

Installation
============

To install this module, you need to:

* Click on install button

Configuration
=============

To configure this module, you need to:

* Set the flag "Automatic" on procurement rule

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
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
stock-logistics-workflow/issues/new?body=module:%20
stock_auto_move%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Nicolas Piganeau <nicolas.piganeau@ndp-systemes.fr>
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
