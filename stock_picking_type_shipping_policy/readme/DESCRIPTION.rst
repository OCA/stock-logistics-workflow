This module adds a Shipping Policy field on Operations Types in order to force
a specific Shipping Policy on Pickings according to their types.

This is especially useful if you use a pick-pack-ship setup with the release
of operation (stock_available_to_promise_release) module along side with
the stock_routing_operation that may split operations by zone of the warehouse.
In that case, you want to be sure the pack operations will wait all different
picks to be processed before releasing the availability of the pack operation.
