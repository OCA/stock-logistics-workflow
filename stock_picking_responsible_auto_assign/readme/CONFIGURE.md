1. Go to *Inventory > Configuration > Operation Types* and open the operation
   type (e.g. *Pick*).
2. In *Responsible Assignment* choose *When the transfer is ready*, add the
   users of the *Responsible Pool* and the *Workload Measure*.
3. Set *Max Pending Transfers per User* to hand out the transfers one (or a
   few) at a time: beyond that number a transfer waits unassigned until a
   user finishes one. Leave 0 to assign everything as soon as it is ready.
4. For a chained operation type (e.g. *Pack*) choose *Together with the
   previous operation*. Either set its own pool, or check *Same Responsible
   as Previous Operation* so the user that picks also packs.
5. On a user form, *Preferences* tab, uncheck *Available for Picking
   Assignment* while the user is absent. The user is skipped until it is
   checked again.
