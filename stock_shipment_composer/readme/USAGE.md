#. Go to *Inventory > Operations > Shipment Composers*.
#. Create a Shipment Composer and set Partner and Operation Type.
#. Add Composer Lines, selecting eligible moves and entering Quantity to ship.
#. Confirm to move to In Progress and confirm underlying pickings.
#. Check Availability to reserve stock.
#. When all lines are sufficiently reserved, Validate. The module fills qty_done,
   propagates dates, posts logs, and validates the pickings.

You can also create Shipment Composers from the stock move list view.

- Go to the stock move list view.
- Select the stock moves that have the same partner and the same picking type for which
  you want to create a Shipment Composer.
- Click Create Shipment Composer under the Action dropdown.

## Business Rules & Behavior

- A picking cannot be validated while any linked composer is active (draft/in_progress).
  Users must validate the composer first.
- Validation sets qty_done = reserved quantities (bounded by line quantity), ensuring
  consistency between reservations and done quantities.
- State is computed from moves; when any move tagged with this composer reaches
  done/cancel, the composer transitions to done and records date_done.
