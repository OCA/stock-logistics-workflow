It allows to define which approach for batch handling will be used per company.
By default after installation this option will be activated for all companies, you can disable
it in settings.

.. figure:: /stock_picking_batch_extended/static/picking_batch_configuration_settings.jpg
   :alt: Picking batch configuration settings
   :width: 80 %
   :align: center

Wizard of add to batch whit the option "a new batch transfer", you can:

* Assign the name of the new batch.
* Add notes to the notes field of the new batch.
* Create a batch with all pickings selected or multiple batch depends on a group field selected in wizard.

.. figure:: /stock_picking_batch_extended/static/stock_picking_list.jpg
   :alt: Sample report template
   :width: 80 %
   :align: center

.. figure:: /stock_picking_batch_extended/static/batch_wizard.jpg
   :alt: Sample report template
   :width: 80 %
   :align: center

After having created a batch with a list of stock picking, you can:

* Allows to rename the batch if it is in the draft status.
* Add field date, on which the batch picking is to be processed.
* Add field notes.
* Add picking count to form view.
* If a batch is cancelled, cancel for all batches pickings and set batches states to cancel too only if user set OCA batch validation approach.
* You can remove all batch pickings from the batch whose status is not done or cancelled.

.. figure:: /stock_picking_batch_extended/static/batch_form.jpg
   :alt: Sample report template
   :width: 80 %
   :align: center

.. figure:: /stock_picking_batch_extended/static/batch_form_operation.jpg
   :alt: Sample report template
   :width: 80 %
   :align: center
