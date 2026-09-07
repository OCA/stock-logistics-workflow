This module allows to declare loss product quantities during picking operations.

When an operator cannot find the whole reserved quantity for an operation, declaring
the loss locks the remaining available quantity of the affected quant (product,
location, lot, package, owner) through a stock move of the warehouse's "Loss" picking
type. This prevents any other operation from reserving that quantity until the loss is
investigated and either confirmed (the lock move is validated) or dismissed (the lock
move is cancelled, releasing the quant back to stock).

The picking is then given the opportunity to still be completed: Odoo looks for the
missing quantity on other available stock (another location or lot). If some is found,
it is reserved on a new operation line, never on one the operator already processed.

This module takes into account the flows with product lot management, packages, owners.
