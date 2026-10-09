A *Quality Check* route is created for each warehouse. It locks quants of
any location of the warehouse with a dedicated *Quality Check* operation type
to the *Quality Check* location of the warehouse. It can be used as is or
adapted, and is the simplest way to start using this module.

To configure other lock routes, you need to:

- Go to *Inventory > Configuration > Routes*.
- Create or open the route that will be used for quant locking.
- Enable *Allow quant lock*.
- Add a *Pull From* rule with the *Take From Stock* supply method. Its source
  location must contain the locations of the quants to lock, its destination
  location and operation type define the lock transfer.

When several rules of the route match the location of a quant, the rule with
the most specific source location is used, then the rule sequence. As for any
rule, the *Propagation of Procurement Group* option of the rule defines how
lock moves are grouped into transfers.

Only routes with *Allow quant lock* enabled can be selected when locking
quants.
