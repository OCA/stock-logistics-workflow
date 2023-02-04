First of all, you need to create your stock device type. To do so, go to the
*Inventory -> Configuration -> Stock Device Types* menu.

Once it's done, you can start creating your picking batches.

To launch the device, go to the *Inventory -> Operations -> Make Picking Batch*
menu.

The *Make Picking Batch* window will open and allows you to specify your criteria
for the batch creation. When all your criteria are set, click on the
*Create Batch Picking* and lets the magic happen. A new window will open with
the created batch picking.

Behind the scene
~~~~~~~~~~~~~~~~

The creation of the picking batch is done in 3 steps:

1. We search for a picking ready to be processed and that fits the
   criteria specified in the wizard.
2. We determine the device to use for this first picking.
3. While the defined limits are not reached, we look for one picking at a
   time that is ready to be processed and that fits the new criteria. The
   new criteria are computed at each loop iteration to take into account
   the pickings already into the batch.

When we look for a picking ready to be processed, we look for a picking
that is in state "Assigned" or "Partially Available" with a picking type
into the list of picking types defined in the wizard and not yet in a batch.

At step 1, we add to theses conditions on the pickings, a list of alternatives
conditions to restrict the search to pickings that can be handled by the device
types defined in the wizard. (A first search is done to try to find a picking
for the given user and which is printed and if not found, we search for pickings
not linked to a user and which are not printed).

At step2, since the first step will return a picking that can be handled by
any of the device types specified, we process the list of device one by one
in the order defined by the sequence field and we stop at the first device
that can handle the picking.

At step 3, now that we have a picking and a device, we have all the information
to refine the search for the next picking to the volume, weight and number of
lines remaining in the batch. While there are still some bins available and
in the batch and the search returns result, we look for a picking that fits
the updated criteria and update the criteria at each loop iteration.

Advanced configuration
~~~~~~~~~~~~~~~~~~~~~~~

Locking
^^^^^^^

You can choice on the wizard to apply a LOCK into the database for each
picking added to the batch. This is useful in a multi-user environment
with a lot of users that can trigger the creation of bach picking to avoid
problems of concurrency. If activated, picking already selected by a concurrent
process will be skipped.

Grouping by partner
^^^^^^^^^^^^^^^^^^^

If you want to allow to group pickings of the same partner into the same
bins, you can activate the option *Group by partner* on the wizard. This
will prevent to consume at least one bin for each picking if pickings
are for the same partner. When activated, the computation of the
number of bins consumed by the picking into the batch will take into account
the volume of the pickings for the same partners already.
