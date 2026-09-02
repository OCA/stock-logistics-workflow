On a transfer, set the *Backorder Policy* (Ask, Always or Never). The value set
here takes precedence over the value set on the operation type; if left empty,
the operation type's value is used.

When the transfer is validated with a missing quantity:

- **Ask**: the usual backorder prompt is shown.
- **Always**: a backorder is created automatically.
- **Never**: the remaining quantity is cancelled.

Returns and exchanges are never subject to the transfer's backorder policy:
they always follow the operation type's own *Create Backorder* setting, since
the policy of the original transfer is not relevant to goods coming back in.
