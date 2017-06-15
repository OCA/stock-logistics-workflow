.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================================
Link between invoices and their pickings
========================================

This module adds a link between pickings and invoices as well as on the lines.
Invoices are generated from sales orders. With this module, you can find back
which deliveries an invoice relates to.

In standard, if you make a partial delivery and invoice it, then make remaining
delivery and invoice it, it is impossible to known to what delivery the
invoices relate to. You only have the quantity.

This module is also useful if you want to present data on the invoice report
grouped by deliveries.

Note that the links are only for products with an invoicing policy set on
delivery.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/9.0

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

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Alexis de Lattre <alexis.delattre@akretion.com>
* Alex Comba <alex.comba@agilebg.com>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Ana Juaristi <anajuaristi@avanzosc.es>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Unai Alkorta
* Iñaki Zabala
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Jacques-Etienne Baudoux <je@bcim.be>

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
