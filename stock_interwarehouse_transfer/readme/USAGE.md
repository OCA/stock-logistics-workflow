Go to _Inventory > Operations > Inter-Warehouse Transfers_ and create a new transfer:

1. Select **From Warehouse** and **To Warehouse** (same company).
2. Optionally override the **From Location** and **To Location** (they default to each
   warehouse's main stock location).
3. Add one or more product lines with quantities.
4. Click **Confirm**.

Two stock pickings are created automatically — an OUT picking at the source warehouse
and an IN picking at the destination warehouse, connected through the company's internal
transit location. Use the **Transfers** smart button to open them.

Validate the OUT picking when the goods leave the source warehouse. The transfer moves
to _In Transit_. Validate the IN picking when the goods arrive at the destination. The
transfer moves to _Done_.

Partial validation creates backorders that are automatically linked to the same transfer
document.

A confirmed transfer stays editable: changing a line quantity, adding a line or removing
one propagates to the stock moves of both legs. The **Shipped** and **Received** columns
show how much of each line is already validated.

- Increasing a quantity extends the open moves. If a leg has no open picking left — for
  instance the OUT was already validated — a new picking is created for the additional
  quantity.
- Decreasing a quantity reduces the open moves, and cancels them when it reaches zero. A
  quantity cannot be decreased below what is already validated on that leg; create a
  return instead.
- Removing a line cancels its moves. A line that is already partly validated cannot be
  removed.

Internal transfers between locations of different warehouses are no longer allowed
outside this document: attempting to create such an internal move raises a validation
error asking to use an Inter-Warehouse Transfer instead.
