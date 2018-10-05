.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

====================================
Stock Picking Operation Quick Change
====================================

This module extends standard WMS to allow change destination location for all
picking operations.


Usage
=====

To use this module, you need to:

#. Go to products and create one of type "Stockable".
#. Update quantities on hand to have stock of it.
#. Go to inventory dashboard and click on "Delivery Orders" card to create a new
   transfer.
#. Create a picking and select the product to do the transfer and save it.
#. Click on button *Change Location*, select in wizard the old location and
   new location.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.
* Open Clipart: `Icon <https://openclipart.org/detail/260861/warehouse15>`__.


Contributors
------------

* Sergio Teruel <sergio.teruel@tecnativa.com>
* Lois Rilo <lois.rilo@eficent.com>

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
