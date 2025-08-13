This module adds a new splitting mode to the stock_split_picking module.

The new mode Quantity of kits allows splitting a transfer by a specified
number of kits. A new field on the wizard also allows specifying a sort
order for the stock moves before splitting the transfer.

Multi level boms are not supported.

When a move needs to be split, it will be unreserved if needed. And
reassigned after the split operation.
