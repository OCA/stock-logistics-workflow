Set options in operation types, you can set 'Auto fill operation' what make
autoassignment button invisible and fill the quantities in operations for lines
and 'Avoid Autoassignment Lots' what allow fill manually the lots quantities.

Products without tracking lots
==============================
After confirming the picking, click on `Auto fill operations` button. The
Operations matching the following conditions will be filled automatically:

* The operation has not be processed (i.e `qty_done == 0`).
* The operation has no package set (i.e `package_id` is empty).

Product with lots
=================
#. Create an outgoing or an internal picking.
#. Include one product with lots and with enough stock.
#. Click on "Mark as Todo" button, and then on "Reserve".
#. Clicking on the icon with the three items bullet list on the "Operations"
   tab you will see that the quantities have been auto-assigned on the "Done"
   column.
