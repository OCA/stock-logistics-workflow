This module adds a quant lock mechanism based on standard stock reservations.
When a quant is locked, its non-reserved quantity is reserved by a dedicated
stock picking so it cannot be consumed by other operations.

The lock operation is done through a selectable operation type (picking type)
explicitly configured for quant locking. Unlocking cancels the lock picking,
which releases the corresponding reservation while keeping full traceability
through standard Odoo stock documents.
