This modules allows to print multiple copies of Delivery Slip report
The new field num_picking_copies on res.partner model indicates how many copies
every partner needs to print the Delivery Slip report.

Also every warehouse have a deliveryslip_folder fields,
if set, when validating a Stock.picking for this warehouse,
Delivery Slip report will be saved to this folder,
the resulting pdf will have as many copies of the report
as set in num_picking_copies partner's field.
