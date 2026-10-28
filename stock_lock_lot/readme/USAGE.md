To use this module, you need to:

1.  Go to *Inventory \> Master Data \> Lots/Serial Numbers*
2.  Select one 'Lot/Serial Number' and check 'Blocked' field
3.  Now you cannot move that 'Lot/Serial Number' to any location that
    does not have the 'Allow Locked' field checked

**Reservation Behavior:**

By default, locked lots are automatically excluded from stock reservations.
When creating outgoing orders (sales orders, transfers, etc.), the system
will only reserve from unlocked lots. This prevents blocked inventory from 
being allocated to orders.

However, you can configure this behavior at the product category level:

- Go to *Sales \> Configuration \> Product Categories*
- In the Warehouse section, check "Allow reservation of locked lots"
- When enabled, locked lots in this category can still be reserved for orders,
  but they cannot be moved unless the destination location allows locked lots

This is useful when you want to:
- Reserve specific inventory for future use but prevent actual movement
- Hold stock for quality inspection while still planning orders

To override this behavior in custom operations, use the 'force_allow_locked_lots' context.

**Example Scenarios:**

- **Quality Hold**: Lock a lot for quality inspection - it won't be reserved
  for customer orders unless the category allows reservation
- **Expired Stock**: Lock expired lots to prevent them from being shipped
