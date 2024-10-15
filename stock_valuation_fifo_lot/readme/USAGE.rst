Process an outgoing move with a lot/serial for a product of FIFO costing method, and the
costs are calculated based on the lot/serial.

You will get a user error in case the lot/serial of your choice (in an outgoing move)
does not have a FIFO balance (i.e. there is no remaining quantity for the incoming move
lines linked to the candidate SVL; this is expected to happen for lots/serials created
before the installation of this module, unless your actual inventory operations have
been strictly FIFO). In such situations, you should select a "rogue" lot/serial (one
that still exists in terms of FIFO costing, but not in reality, due to the inconsistency
carried over from the past) in the 'Force FIFO Lot/Serial' field so that this lot/serial
is used for FIFO costing instead.
