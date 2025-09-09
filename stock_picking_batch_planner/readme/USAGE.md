To use this module, you need to:

Sale Flow:

1. Go to Inventory > Configuration > Warehouses, select one warehouse and choose deliver in 2-steps.
1. Go to Inventory > Configuration > Operation Types, choose *Pick*, select "Plan Origin" and select your criteria for Batch/Wave grouping.
1. Go to Sales > Orders > Orders, create some sale orders and confirm them.
1. Go to Inventory > Operations > Jobs > Batch transfers and create a new batch.
1. Add pickings of type delivery created from confirm the sales orders.
1. A button **Plan Batches** is displayed if the moves in the batch have origin moves and the origin pickings can be grouped in batches or origin move lines can be grouped in waves .
1. When you click on this button, the origin move lines will be batched according to the criteria configured in operation types.
1. If the batch has origin batch/wave, a smart button is displayed.
