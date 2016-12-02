.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Stock Packaging Info
====================

This module displays in the picking_ids, all packages appearing in operations and
the package provides the following information:

* Width
* Height
* Length
* Total estimated weight
* Total estimated net weight
* Permitted volume
* Total volume charge
* Empty package weight
* Real weight


Usage
=====

At first, when a logical unit is provided for the package, it will take width,
height, length and empty weight, but it can be specified one for the package.

In the field "real weight", shown the value of total estimated weight field.
The value of this field can be changed.

In the transfer wizard picking_ids, you have a new button "Save for later", that
allows only modify datas of operations of the picking.

Also, this module displays in the picking_ids, the number of packages per logistic
unit, and kg. and lots by package.


You can print labels of pallets.

Known issues / Roadmap
======================

* Computed fields in `stock.picking` are not stored because the dependant field
is an O2M relation that is never implicitly set via ORM or views.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <anajuaristi@avanzosc.es>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Brett Wood <bwood@laslabs.com>
* Dave Lasley <dave@laslabs.com>
* Ted Salmon <tsalmon@laslabs.com>

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
