To use this module, you need to:

1.  Go to *Inventory \> Master Data \> Lots/Serial Numbers*
2.  Select one 'Lot/Serial Number' and check 'Blocked' field
3.  Now you cannot move that 'Lot/Serial Number' to any location that
    does not have the 'Allow Locked' field checked

**Reservation Behavior:**

- Locked lots are automatically excluded from stock reservations
- When creating outgoing orders (sales orders, transfers, etc.), the system
  will only reserve from unlocked lots
- This prevents blocked inventory from being allocated to orders
- To override this behavior, use the 'force_allow_locked_lots' context in
  custom operations when explicitly needed

**Example Scenarios:**

- **Quality Hold**: Lock a lot for quality inspection - it won't be reserved
  for customer orders until unlocked
- **Expired Stock**: Lock expired lots to prevent them from being shipped
- **Reserved Stock**: Lock lots for specific customers or projects
