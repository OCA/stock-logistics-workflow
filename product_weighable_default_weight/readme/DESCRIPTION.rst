This module extends the functionality of product module to set
default value on weight field for weighable products.

Once installed, when a user create a new weighable product
(``uom_id.measure_type == "weight"``), the ``weight`` field
will be computed, depending on the UoM.

- if UoM is "kg", weight will be 1.0
- if UoM is "ton", weight will be 1000.0

This module is interesting if you use other modules based on the
``weight`` field. (Ex: ``sale_order_weight`` in OCA/sale-workflow repo)
