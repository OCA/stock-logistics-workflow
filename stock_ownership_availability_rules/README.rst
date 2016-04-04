.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================
Stock Ownership Availability Rules
==================================

This module extends the core behaviour to manage ownership of stock. It is
useful when we want to keep stock that belongs to someone other than our
company.

This functionality is partially implemented in Odoo, with some missing
behaviour (e.g. it will silently deliver someone else's stock if that's all
we've got).

The purpose of this module is also to add tests that are missing in the Odoo
core.

With this module, the owner of quants becomes required, and is set by default
as follows:

- If the location of the quant has a partner, it is used.
- Otherwise, if the location of the quant has a company, the related partner is
  used.
- Otherwise, the partner related to the default company for quants is used.

The tests make sure that the quants reservation always respect owners:

- Outgoing pickings without owner or with company owner only reserve quants
  with company owner, otherwise they remain unreserved.
- Outgoing pickings with owner only reserve quants with the same owner,
  otherwise they remain unreserved.

To understand stock owners more easily, now the "On Hand" button on the product
form view opens a stock view grouped by location and owner (instead of location
only).

Partially related to this is issue https://github.com/odoo/odoo/issues/4136.

Usage
=====

To use this module, you need to:

* Go to ...

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
stock-logistics-workflow/issues/new?body=module:%20
stock_ownership_availability_rules%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Leonardo Pistone <leonardo.pistone@camptocamp.com>
* Laurent Mignon <laurent.mignon@acsone.eu>

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
