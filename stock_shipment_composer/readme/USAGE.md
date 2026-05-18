1. Go to *Inventory > Operations > Shipment Composers*.
2. Create a Shipment Composer and set Partner and Operation Type.
3. Add Composer Lines, selecting eligible moves and entering Quantity to ship.
4. Confirm to move to In Progress and confirm underlying pickings.
5. Check Availability to reserve stock.
6. When all lines are sufficiently reserved, Validate. The module sets the move
   quantities to the line quantities, posts logs, and validates the pickings.

You can also create Shipment Composers from the stock move list view:

1. Go to the stock move list view.
2. Select the stock moves that have the same partner and the same picking type for
   which you want to create a Shipment Composer.
3. Click Create Shipment Composer under the Action dropdown.

## Business Rules & Behavior

- A picking cannot be validated while any linked composer is active
  (draft/in_progress). Users must validate the composer first.
- Validation sets each move's quantity to its line quantity and marks it as picked,
  so only the composed quantities are processed.
- State is computed from moves; when any move tagged with this composer is done, the
  composer transitions to done and records date_done. When all its moves are
  cancelled, the composer is cancelled.
