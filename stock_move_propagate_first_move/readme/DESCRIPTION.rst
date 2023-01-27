Sometimes when you process your move, you need to know which move has
been at the origin of the procurement chain that lead to the creation
of the move. This information could be useful for example to know
if the move is part of an outgoing or incoming process without having
to look at the chained moves.

This module add the fields `first_move_id` and `first_picking_type_id` on the
move line to give this information in a transparent way without having
to wonder about the direction in which the move chain should be navigated
to get the information.
