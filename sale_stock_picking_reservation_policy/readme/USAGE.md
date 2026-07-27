On a contact, set a *Reservation Policy* (Partial or All or nothing per line). It
is shared with the contact's delivery addresses.

On a sale order, the *Reservation Policy* defaults from the customer (or delivery
address) and can be adjusted manually before confirmation.

When the order is confirmed, the policy is carried over to the deliveries it
generates. On those deliveries:

- **Partial**: each line reserves whatever quantity is available.
- **All or nothing per line**: each delivery line (stock move) is reserved only
  if its full quantity is available from stock; otherwise that line stays
  unreserved. The rule is applied independently on each line, not on the delivery
  as a whole.
