Stock Dropshipping Dual Invoice
===============================

This module allows to handle a case which does not work on Odoo 8.0: a drop
shipping delivery where the attached sale and purchase are both invoiced on
delivery.

The wizard to generate the invoice has been modified to ask for the two
journals to use for the two invoices that will be created.

The generated customer and supplier invoices are then linked to the sale and
purchase, respectively.

See also the discussion on odoo/odoo#4131.

Usage
=====

- Choose a product that has a supplier.
- Create a Sale of the product. Choose in the line the Drop Shipping route,
  and choose to invoice in delivery.
- Find the automatically generated RFQ, in it specify invoicing on
  delivery, and validate.
- Open the delivery, transfer it, and click the button to generate the
  invoice.
- Fill in the wizard. Two invoices will be generated -- one for the customer,
  one for the supplier.
- You can find the generated customer and supplier invoices from the Sale and
  Purchase Orders, respectively.

Known issues
------------

When the wizard creates a supplier invoice and a customer invoice, it does not
show them, and instead the wizard is simply closed, going back to the picking.
This is because we cannot easily show a customer and a supplier invoice
together in a tree view, because one of them would not get the correct form
view.

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
