Technical module. It adds hooks to the core putaway method
``StockLocation._get_putaway_strategy()`` allowing to plug other strategies and
makes the selector fields in the tree views dynamic (required/readonly). See the
usage section for details.

An example of implementation is the module ``stock_putaway_by_route``.
