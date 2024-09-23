This modules adds the possibility to define delays in workable days for pull and buy stock rules.
Also, this modules ensures that the expected expiration date of the products is compatible with
the planned consumed date of the sale order at confirmation.

More specifically, this module:
- Adds working schedules to the warehouses.
- Adds working schedules to the suppliers.
- Adds a check box for pull stock rules to specify whether the delay defined is in workable days
- Adds lead times per day of the week for buy rules, plus a checkbox to specify whether
the lead times are in workable days.

When delays are defined in workable days, the system will take into account the working schedules of both,
the source location warehouse schedule and the destination location warehouse schedule to plan the stock pickings.
For buy rules, the system will take into account the working schedule of the supplier and the reception location warehouse schedule to create the purchase order.
