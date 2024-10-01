This module adds a constraint on stock.move.line to make sure that no
stock exists for the specified serial 1) when serial is input (in
lot_name field), and 2) when the lot is being created (in
\_action_done()) in purchase receipts, to avoid duplicates.

Standard behavior fails to prevent the duplicates, for example, when
there is stock for a serial with no owner, and new stock comes in with
the same serial with an owner. This module intends to cater to this
case.
