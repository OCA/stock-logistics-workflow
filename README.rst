MRP lock lot
============
* This module allows you to define whether a lot is locked or not. By default,
  the value that will catch, which will define in Configuration - Configuration
  - Warehouse, in the field "Create in locked status when create a lot".
* To lock/unlock a lot, have created 2 new buttons in form. Also from the tree
  view, by selecting the lots in option "Lock/Unlock lots".
* When you lock one lot, validates that does not exist a quant assigned to the
  lot, or if exist the quant assigned to the lot, that there is no movement of
  stock, with different state to "done", and with destination location type
  virtual/company.
* Changes in manufacturing, and delivery orders, to selecting the locked
  bundles is prevented.

Credits
=======

Contributors
------------
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com
* Ana Juaristi <ajuaristo@gmail.com>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
