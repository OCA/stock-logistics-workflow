Stock picking partial invoicing
===============================

This module was written to extend the invoicing capabilities of Odoo,
and allows users to create customer or supplier invoices for part of
a delivered Order or received Incoming Shipment.


Installation
============

This module depends on the module 'report_xls', available in
https://github.com/OCA/reporting-engine


Configuration
=============

This module does not require any additional configuration.

Usage
=====

When the user wants to create an invoice for a Delivery Order or
Incoming Shipment she/he can indicate which moves should be invoiced,
and what quantity to invoice.

Known issues / Roadmap
======================

This module conflicts with module 'stock_picking_invoice_link' available in
the same OCA repository.

Credits
=======

Contributors
------------

* Jordi Ballester <jordi.ballester@eficent.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.