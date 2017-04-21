.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Partner Credit Limit
====================

This module prevents users from shippings orders that would put customers above their credit limit based on open invoices.

It adds a new group that allows certain users to manage credit hold of the customers.

After this module is installed, credit limits will be verified for all customers.

Innstallation
=============

* No specific installation required.

Configuration
=============

* Add allowed users to the 'Credit Hold' group

Usage
=====

* Create a customer, set his salesperson and verify that 'Sales Hold' is
  checked.
* Set his credit limit, his payment terms and grace period.
* Create a quotation for the customer within his credit limit. Confirm it and
  verify that you cannot ship it

  * Uncheck 'Sales Hold' and verify that you can now ship it.
  * Generate the invoice and confirm it.

* Create a quotation for the customer to go over his credit limit. Confirm it
  and verify that you cannot ship it.
* Create a quotation for the customer within his credit limit

  * Confirm it and generate the invoice but change the invoice date to be over
    his payment term and grace period.
  * Validate the invoice and verify that you cannot ship the order.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Adam O'Connor <aoconnor@ursainfosystems.com>
* Sandeep Mangukiya <smangukiya@ursainfosystems.com>
* Maxime Chambreuil <mchambreuil@ursainfosystems.com>
* Balaji Kannan <bkannan@ursainfosystems.com>
* Bhavesh Odedra <bodedra@ursainfosystems.com>

Funders
-------

The development of this module has been financially supported by:

* Ursa Information Systems <http://www.ursainfosystems.com>

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
