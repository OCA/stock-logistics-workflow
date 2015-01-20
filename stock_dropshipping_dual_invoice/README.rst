Stock Dropshipping Dual Invoice
===============================

This module allows to handle a case which does not work on Odoo 8.0: a drop
shipping delivery where the attached sale and purchase are both invoiced on
delivery.

The wizard to generate the invoice has been modified to ask for the two
journals to use for the two invoices that will be created.

See also the discussion on odoo/odoo#4131.

Known issues
------------

The wizard does create a supplier invoice and a customer invoice, but in order
to see them correctly, the user has to open them via the "Customer Invoices"
and "Supplier Invoices" menu. That is because they have two different form
views.

Credits
=======

Contributors
------------

* Leonardo Pistone <leonardo.pistone@camptocamp.com>

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
