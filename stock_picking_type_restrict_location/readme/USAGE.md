On the transfers of a restricted operation type:

- The **Source Location** and the **Destination Location** only offer the
  locations of the operation type and their sublocations.
- A transfer with any other location is rejected with a blocking message, also
  when it is not created by hand.
- A return created from a transfer can go back the way that transfer came, even
  when it uses the same operation type: its source can be inside the
  destination of the original transfer, and its destination inside the source
  of the original transfer.
- When the source or the destination of the operation type is a vendor or a
  customer location, that side of the transfer is not restricted.

Transfers that are done or cancelled are not checked.

The rules of a restricted operation type cannot take stock from locations
outside its source location. Their destination is checked when it becomes the
destination of the transfer: on push rules, except the ones that add no step,
and on rules that take the destination location from the rule. Pull rules that
send stock to a production location are not checked: they describe the
components consumed by manufacturing orders, not transfers.

The transfers of the other operation types keep the standard behavior.
