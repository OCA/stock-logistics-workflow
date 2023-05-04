This module is based on `picking_dispatch <https://github.com/OCA/stock-logistics-workflow/tree/8.0/picking_dispatch>`_
but reworked for matching Odoo new picking system (with pack operations).

Since v12 it is compatible with odoo addon https://github.com/odoo/odoo/blob/12.0/addons/stock_picking_batch/models/stock_picking_batch.py
It allows to define which approach for batch handling will be used per company.
By default after installation this option will be activated for all companies, you can disable
it in settings.

Batch picking allows you to manage several pickings at the same time.
You can create a batch with all pickings selected or multiple batch depends on
a group field selected in wizard.

After having created a batch with a list of stock picking, you can:

* Check availability and reserve quants for all pickings
* Mark all pickings as done when delivery is done.
* Make partial delivery by filling done quantities in pack operations tab.
* Print a report to pick the proper goods at once

.. figure:: https://raw.githubusercontent.com/OCA/stock-logistics-workflow/11.0/stock_batch_picking/static/stock_picking_list.png
   :alt: Sample report template
   :width: 80 %
   :align: center

.. figure:: https://raw.githubusercontent.com/OCA/stock-logistics-workflow/11.0/stock_batch_picking/static/batch_wizard.png
   :alt: Sample report template
   :width: 80 %
   :align: center

.. figure:: https://raw.githubusercontent.com/OCA/stock-logistics-workflow/11.0/stock_batch_picking/static/batch_form.png
   :alt: Sample report template
   :width: 80 %
   :align: center

.. figure:: https://raw.githubusercontent.com/OCA/stock-logistics-workflow/11.0/stock_batch_picking/static/batch_form_operation.png
   :alt: Sample report template
   :width: 80 %
   :align: center
