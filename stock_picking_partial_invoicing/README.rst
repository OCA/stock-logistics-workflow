Stock picking partial invoicing
===============================

This module was written to extend the invoicing capabilities of Odoo,
and allows users to create customer or supplier invoices for part of
a delivered Order or received Incoming Shipment.


Installation
============

No installation instructions are required.


Configuration
=============

This module does not require any additional configuration.

Usage
=====

When the user wants to create an invoice for a Delivery Order or
Incoming Shipment she/he can indicate which moves should be invoiced,
and what quantity to invoice.

If the system identifies that the stock move has been fully invoiced, it
will change the corresponding status.

If the user deletes the invoice or an invoice line, the corresponding stock
move changes to the status 'To be invoiced'.

If the user changes the quantity in the invoice, the invoice control in
the stock move will not be changed. This allows for more flexibility (e.g.
the company will not accept an invoice for some products that were
received with defects).


Known issues / Roadmap
======================

No issues have been identified.

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