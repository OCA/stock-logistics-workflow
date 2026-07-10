This module adds a *Restrict Partial Validation* option on operation types.

Transfers of a restricted operation type can only be validated when they are
fully reserved and processed in full:

- Validation is blocked while the transfer is not in *Ready* state, so
  quantities cannot be forced on stock that is not reserved.
- Validation is blocked when any line is processed for less than the demanded
  quantity, so no backorder can ever be created for these transfers.

A typical use case is all-or-nothing internal transfers, such as kit
transfers that must always travel complete. Combined with the *When all
products are ready* shipping policy, operators only see these transfers as
Ready when everything can be moved, and cannot process them any other way.