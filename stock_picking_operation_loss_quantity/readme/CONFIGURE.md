- Go to Inventory > Configuration > Settings > Warehouse
- Enable 'Storage Locations' and 'Multi-Step Routes'.
- Go To Inventory > Configuration > Warehouse Management > Warehouses
- On the selected Warehouse, check the 'Enable the Loss feature' under 'Loss' section.
  This automatically creates a dedicated 'Loss' operation type for the warehouse, with
  the 'Allow quant lock' option (from the `stock_quant_lock` module this module depends
  on) enabled and a destination location set.

This module relies on `stock_quant_lock` to actually lock the quant when a loss is
declared: locking is only possible on an operation type that has 'Allow quant lock'
enabled and a destination location configured. If the warehouse's 'Loss' operation type
is later edited (Inventory > Configuration > Operations Types) and either of these is
removed, declaring a loss will fail with an error.