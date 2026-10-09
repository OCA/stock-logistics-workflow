- Go to Inventory > Configuration > Settings > Warehouse
- Enable 'Storage Locations' and 'Multi-Step Routes'.
- Go To Inventory > Configuration > Warehouse Management > Warehouses
- On the selected Warehouse, check the 'Enable the Loss feature' under 'Loss' section.
  This automatically creates a dedicated 'Loss' operation type, a 'Loss Control'
  location and a 'Loss Route' for the warehouse. The route has the 'Allow quant lock'
  option (from the `stock_quant_lock` module this module depends on) enabled and a
  pull rule from the warehouse to the 'Loss Control' location using the 'Loss'
  operation type.

This module relies on `stock_quant_lock` to actually lock the quant when a loss is
declared: the quant is locked by a procurement on the warehouse's 'Loss Route'. If
this route is later edited (Inventory > Configuration > Routes) and either the 'Allow
quant lock' option or its pull rule is removed, declaring a loss will fail with an
error. The rule can be adapted, for example to change the operation type or the
destination of the loss transfers.