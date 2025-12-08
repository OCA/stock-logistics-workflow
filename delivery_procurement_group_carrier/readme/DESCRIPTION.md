This is a base module that propagates the SO carrier to the procurement
group.

Having the carrier on the procurement group allows to apply different
routing for each carrier thanks to the dynamic routing. A rule domain
can then be expressed based on the delivery carrier. See the module
stock_dynamic_routing in OCA/wms.

The carrier on the procurement group is also used for grouping several
SO in a same delivery by carrier. See the module
stock_picking_group_by_partner_by_carrier in this repository.
