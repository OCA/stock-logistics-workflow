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


Contributors
------------

* Leonardo Pistone <leonardo.pistone@camptocamp.com>
* Alex Comba <alex.comba@agilebg.com>
