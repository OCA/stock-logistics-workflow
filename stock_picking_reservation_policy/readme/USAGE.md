To set the default reservation policy of an operation type:

1. Go to *Inventory > Configuration > Operations Types*.
2. Open an operation type and set its *Reservation Policy* (Partial or All or
   nothing per line).

On a transfer, the *Reservation Policy* defaults from the operation type and can
be adjusted manually before reservation.

When checking availability:

- **Partial**: each line reserves whatever quantity is available.
- **All or nothing per line**: each transfer line (stock move) is reserved only
  if its full quantity is available from stock; otherwise that line stays
  unreserved, leaving its stock available to the other lines. The rule is applied
  independently on each line, not on the transfer as a whole.
