Transfers and batches are often exchanged with third parties, such as a
warehouse management system (WMS) or a carrier, which refer to the lines by
a position and send it back in their confirmations. Such a reference must not
change once it has been sent, unlike the `sequence` used to order the lines.

`stock_picking_line_sequence` also numbers the moves of a transfer, with an
integer used to order them. This module gives stable references instead, on
transfers and on batches.
