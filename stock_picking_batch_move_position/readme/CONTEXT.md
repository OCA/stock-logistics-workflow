A batch transfer groups the moves of several transfers, which can share the
same position (see `stock_move_position`): each transfer numbers its moves on
its own. When a batch is exchanged with a third party, such as a warehouse
management system (WMS), its lines need a reference that is unique in the
batch and that does not change once it has been sent.
