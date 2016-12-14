.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Procurement Select Route
========================

In Odoo, if you select 2 possible routes on a product (e.g. Buy and Manufacture),
when processing the procurement order, the system will select one route
or the other based on the sequence numbers on the routes/rules.

This module prevents this behavior. If more than one route is defined on the
product (or product category), the procurement order will fall in exception state.
Then, the user will be asked to select one of the routes directly on the
procurement order form. When restarting the procurement order, the system will use the
route selected by the user.

This module's main use case is to allow the user to manually handle the choice
between producing an item and taking it from the inventory.

This module is relevant when the decision of which route to use is made by the
warehouse staff. Otherwise, in native Odoo, the route could be defined directly
on the sale order line before confirming the sale.


Usage
=====

To use this module, you need to:

#. Create a product
#. Select 2 routes on the product
#. Create a sale order with the new product on one line
#. Confirm the sale order
#. Go to: Inventory -> Reports -> Procurement Exceptions
#. Select the procurement order related your sale order
#. Select a route in the field 'Product Route'
#. Click on 'Run' and your procurement order should pass to the state 'Running'

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/9.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/purchase-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>

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
