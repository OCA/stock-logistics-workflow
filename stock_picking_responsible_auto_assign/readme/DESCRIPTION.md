This module assigns the responsible of a transfer automatically, balancing
the pending workload between the users of a pool defined per operation type.

When a transfer becomes ready it goes to the user of the pool with the lowest
pending workload (number of lines, quantity or number of transfers, as
configured). A big order keeps its user busy while the others receive the
small ones, so the work is spread by effort and not by count.

The work can also flow as a queue: with a maximum of pending transfers per
user (e.g. one), a transfer beyond that limit waits unassigned and is handed
out, most urgent first, when a user finishes one.

Chained operations can be assigned together: when a pick transfer gets its
responsible, the following pack transfer can get its own responsible at the
same time, either balanced within the pack pool or copied from the pick.
The picker then knows from the start who will pack the goods.
