Relocate source location of unconfirmed moves

Add relocation rules for moves.

Some use cases:

* Handle all the replenishments at the same place
* Trigger minimum stock rules or DDMRP buffers in one location

Behavior:

* When we try to assign a stock move and the move is not available, a rule
  matching the source location (sub-locations included), the picking type and an
  optional domain is searched
* If a relocation is found, the move source location is updated with the new one
* If the move was partially available, it is split in 2 parts:

 * one available part which keeps its source location
 * one confirmed part which is updated with the new source location

Notes:

Goes well with ``stock_available_to_promise_release``.
When using the mentioned module, we assume that we release moves (which
creates the whole chain of moves) only when we know that we have the
quantities in stock (otherwise the module splits the delivery). So generally,
we have the goods are available, but maybe not at the correct place: this
module is handy to organize internal replenishments.

Compatible with ``stock_dynamic_routing``: when the source location is updated
by this module, a dynamic routing may be applied.
