This module can be used if your customers expect that several different orders
they passed will be shipped in a single delivery order.

With this module installed, when a sale order is confirmed, the stock moves for
the lines of the sale order can be placed in an existing delivery order that
shares the same delivery address and carrier (or lack thereof).

Sale orders with a Shipping Policy set to 'When all products are ready' always
get their own shipping.

When the delivery slip is printed, the list of pending quantities to deliver
is shown at the end, grouped by order.

The grouping can also be applied in case of external resupply. Moves at the
destination of the same delivery address defined on the resupply stock rule
will be grouped in a same delivery order.

Note: The grouping is currently not propagated to the pulled internal moves if
you don't use the module stock_available_to_promise_release in the wms
repository.
