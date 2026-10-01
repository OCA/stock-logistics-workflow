**Business Need**

Companies with multiple warehouses sometimes need to initiate stock transfers
based on an operational decision — not triggered by procurement demand. Typical
use cases:

- Proactively balancing inventory between locations.
- Reviewing and confirming both the outgoing and incoming legs before any stock
  moves.
- Tracing the full inter-warehouse operation as a single document.

Odoo's standard resupply routes are demand-driven and do not provide a single
document grouping both legs of a transfer.

**Approach**

On confirmation, the transfer creates exactly two pickings connected through the
company's internal transit location: an **OUT** picking at the source warehouse
and an **IN** picking at the destination warehouse. Both use dedicated operation
types (`IW` / `IWR`) created lazily per warehouse, keeping inter-warehouse moves
out of regular delivery and receipt queues.

The OCA module `stock_warehouse_resupply_route_push` (v18.0+,
`OCA/stock-logistics-workflow`) provides a similar capability via push rules,
but the IN picking is only created after the OUT picking is validated — making
it impossible to review both legs before stock moves.

**Useful Information**

- Requires an **Internal Transit Location** configured on the company
  (`Inventory > Configuration > Warehouses`).
- Designed for single-company, multi-warehouse setups.
- Source and destination locations default to each warehouse's main stock
  location and can be overridden per transfer.
- Works with Odoo's standard backorder flow: partial validations create
  backorders automatically linked to the same transfer document.
