When grouping orders and using cut-off dates
you must group orders by date as well, to not end up w/ tons of orders.

Basically this is a dumb glue module between

1. stock_picking_group_by_partner_by_carrier
2. sale_cutoff_time_delivery
3. stock_picking_group_by_partner_by_carrier_by_date

which makes sure module 3 is installed when 1 and 2 are.
