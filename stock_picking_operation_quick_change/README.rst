.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

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
#. Go to inventory dashboard and click on "Delivery Out" card to do a new
   transfer.
#. Create a picking and select the product to do the transfer.
#. Reserve the picking.
#. Click on button *Change Location*, select in wizard the old location and
   new location.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/9.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/154/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/
  blob/master/template/module/static/description/icon.svg>`_.
* Open Clipart: `Icon <https://openclipart.org/detail/260861/warehouse15>`_.


Contributors
------------

* Sergio Teruel <sergio.teruel@tecnativa.com>

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
