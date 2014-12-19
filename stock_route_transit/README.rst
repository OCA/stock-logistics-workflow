Stock Route Transit
===================


This addon adds Transit route configuration facility for warehouses by adding
new possible values for the reception_steps and delivery_steps fields of
stock.warehouse. It does nothing that could not be done manually, but the
manual configuration of these routes is long, tedious and error prone, which is
why the reception_steps and delivery_steps fields were added in the first place
in Odoo.

When configuring a reception (resp. delivery) with transit, the goods shipped
by the supplier (rest. to the customer) first go to a transit stock.location
before reaching their final destination. This allows for tracking the shipping
date separately from the delivery date, as well as managing incidents which can
occure during transport.

Contributors:

* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Joël Grand-Guillaume <joel.grandguillaume@camptocamp.com>
