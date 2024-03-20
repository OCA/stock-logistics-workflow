This module was developed because the modules **sale_elaboration** and **stock_customer_deposit** create a compute method for the order line *route_id* field.

As odoo does not have a compute core method for this field, it cannot be inherited so if you install both modules, one method will be overwritten and one behaviour will be lost.
