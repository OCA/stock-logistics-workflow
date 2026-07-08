To set a partner's backorder policy:

1. Open the contact form and go to the *Sales & Purchase* tab.
2. Set a *Backorder Policy* (Ask, Always or Never). It is shared with the
   contact's delivery addresses.

On a transfer, the *Backorder Policy* defaults from the partner and can be
adjusted manually. The value set here takes precedence over the value set on
the operation type; if left empty, the operation type's value is used.

When the transfer is validated with a missing quantity:

- **Ask**: the usual backorder prompt is shown.
- **Always**: a backorder is created automatically.
- **Never**: the remaining quantity is cancelled.

Returns and exchanges are never subject to the partner/transfer backorder
policy: they always follow the operation type's own *Create Backorder*
setting, since the customer-facing policy is not relevant to goods coming
back in.
