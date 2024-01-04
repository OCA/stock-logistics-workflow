Improve the standard process of changing a lot on a move line.

When changing a lot on a move line, check available quantity and, if necessary,
switch reservation with other moves lines.

It never "steal" for already picked lines (quantity done > 0).
However, it can switch with pickings already printed. This is required for
drill-through locations where you need to invert the reservations.

If the new lot only matches partially the initial reserved quantity, the
reservation of this line will decrease to match what is available and a new
move line will be created to recover the missing quantity.

