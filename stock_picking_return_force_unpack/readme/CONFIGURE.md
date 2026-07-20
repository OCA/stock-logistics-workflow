1. Navigate to **Inventory > Configuration > Operations Types**.
2. Select the incoming Operation Type that returns/exchanges of the
   relevant deliveries will resolve to.
3. Check the box "Force Unpack on Return" and save.

Note that a return or exchange picking is not necessarily created with the
same operation type as the picking being returned: Odoo resolves it through
`Return Type` (`return_picking_type_id`), which for a standard warehouse is
the matching incoming/outgoing type. Enable the option on that resolved
operation type, not necessarily on the one you are returning from.
