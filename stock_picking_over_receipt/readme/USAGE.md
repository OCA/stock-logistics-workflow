Splitting a receipt: the lines received above their demand are not split.
They stay whole on the receipt with their received quantity, and only the
open remainder of the other lines goes to the new receipt. A receipt with
nothing left open (every line received in full or above) still cannot be
split.

Validating a receipt with lines received above their demand schedules a To-Do
activity "Received above demand" on it, listing those lines with their
received and demanded quantities. The activity goes to the Responsible of the
receipt or, when it has none, to the user who created the receipt (the
original receipt, for a backorder).
