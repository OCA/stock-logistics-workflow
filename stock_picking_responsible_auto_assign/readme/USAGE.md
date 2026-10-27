Nothing has to be done: the responsible is set when the transfer is reserved
(check availability, scheduler, order confirmation or backorder creation).

A responsible set by hand to a user of the pool is respected. A responsible
outside the pool (the salesperson that confirmed the order, the scheduler) is
replaced.

With a maximum of pending transfers per user, the transfers waiting for a
responsible are the ready ones without responsible. They are handed out when
a transfer is validated or cancelled, or when a user becomes available again.

The transfer shows its *Progress* (picked lines over total lines) and is
*In Progress* once the operator picked a line, e.g. by scanning it in the
barcode app. The *In Progress* filter lists them.

To redistribute the work, select the transfers in the list and run
*Reassign Responsible*, or use the same action on the transfer form. It
ignores the current responsible and picks the least loaded available user,
but skips the transfers in progress: to take one away from its operator,
change the responsible by hand.

The field *Next Operation Responsible* on the transfer shows who is in charge
of the following chained transfer (e.g. who packs what is being picked).
Changing it there changes the responsible of that transfer.
