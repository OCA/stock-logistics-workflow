This module enables the capability to manage the priority of a stock move
directly on the move itself. The goal is to promote/demote specific moves.

Into the reserving process, the moves are sorted by reservation date, then priority,
then date and finally by sequence. By default, the only way to change the priority
of a move is to change the priority of the picking.  If this default behavior fits
for most of the cases, we can imagine that in some cases, we want to change the
priority of a move without changing the priority of the picking since the stock is
limited for this particular product and we want to be sure that the move will be
reserved before others created before this one for example. This addon allows you
to do it by displaying the priority field into the Operations tree of the picking
form view.
