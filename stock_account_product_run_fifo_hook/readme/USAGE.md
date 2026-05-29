1. Add dependency of this module to your custom module:
   ```python
   "depends": ["stock_account_product_run_fifo_hook"],
   ```

2. Inherit from `product.product` in your custom module

3. Override the hook methods to add custom logic:
   - `_run_fifo_prepare_candidate_update(candidate_move, qty_taken, value_taken, valued_move=None)` — Called for each FIFO candidate when it is consumed. 
     - `candidate_move`: The FIFO source move being consumed
     - `qty_taken`: Quantity consumed from this candidate
     - `value_taken`: Value consumed from this candidate
     - `valued_move`: (obtained via context) The stock move being valued that is consuming this candidate
     
     Use it to capture exact qty/value taken, create usage records, or track valuation relationships between moves.

## When `valued_move` is Passed to Context

The `valued_move` is passed to context when an outgoing stock move calls `_set_value()` for FIFO costing:

```python
# In stock.move._set_value() for FIFO moves:
for move in fifo_moves:
    super(StockMove, move.with_context(valued_move=move))._set_value(
        correction_quantity=correction_quantity
    )
```

This happens when:
1. An outgoing stock move (customer delivery, internal transfer, etc.) is being valued
2. The product uses FIFO costing method
3. The system needs to consume FIFO candidates to determine the move's valuation

During this process:
- `_run_fifo()` is called to calculate the unit cost
- For each FIFO candidate consumed, `_run_fifo_prepare_candidate_update()` hook is called
- The `valued_move` (the move being valued) is available in context
- You can use it to link the candidate to the move being valued
