In some situations, you need to create the stock movement with a certain priority
(e.g.: the stock_location_orderpoint module (in OCA/wms)) and create the picking
with that priority.

In core, Odoo compute the priority on move level depending on picking priority
value.
