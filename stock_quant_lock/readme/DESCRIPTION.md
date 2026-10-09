This module adds a quant lock mechanism based on standard stock reservations.
When a quant is locked, its non-reserved quantity is reserved by a dedicated
stock picking so it cannot be consumed by other operations.

The lock operation is done by running a procurement on a selectable route
explicitly configured for quant locking: the pull rule of the route defines
the operation type, the destination and the grouping of the lock transfer. Unlocking cancels the lock picking,
which releases the corresponding reservation while keeping full traceability
through standard Odoo stock documents.
