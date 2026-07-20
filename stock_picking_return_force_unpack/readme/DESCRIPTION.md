Ensures returns and exchanges are not left stuck in the package they were
originally shipped in.

When a delivery was validated with "Put in pack" and only part of the
quantity is later returned, the return operation can inherit the original
package as both its source and destination package assignment. If that
package still holds the remaining, non-returned units at the customer,
forcing the return to also arrive back into that same package elsewhere
fails validation with an error about moving a container between locations.

This module adds a **Force Unpack on Return** option on the Operation Type.
When enabled on the operation type used for a return or exchange, the
destination package assignment is automatically stripped from that return's
stock moves, so the returned quantity is received unpackaged instead of
recreating the original container.

The source package assignment is intentionally left untouched: Odoo still
needs it to resolve the move against the exact quant being returned. This
matters in particular for lot/serial tracked products, where clearing the
source package too would leave the original quant untouched inside its
package at the customer while creating an unrelated, unpackaged quant at the
destination -- two quants for the same serial number instead of one moving.
