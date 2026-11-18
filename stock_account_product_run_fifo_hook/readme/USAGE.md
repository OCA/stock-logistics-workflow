1. Add dependency of this module to your custom module:
   ```python
   "depends": ["stock_account_product_run_fifo_hook"],
   ```

2. Inherit from `product.product` in your custom module

3. Override the hook methods to add custom logic:
   - `_run_fifo_prepare_candidate_update(candidate_move, qty_taken, value_taken, valued_move)` — Called for each FIFO candidate when it is consumed. 
     - `candidate_move`: The FIFO source move being consumed
     - `qty_taken`: Quantity consumed from this candidate
     - `value_taken`: Value consumed from this candidate
     - `valued_move`: The stock move being valued that is consuming this candidate (`None` when core estimates a FIFO price without valuing a move)
     
     Use it to capture exact qty/value taken, create usage records, or track valuation relationships between moves.

## When `valued_move` is Passed to Context

This module sets `valued_move` when `stock.move._set_value()` values an outgoing FIFO
move, keeping the core batch valuation of all the moves.

The hook is called:

- after the outgoing move is done (moves are valued after `_action_done()`)
- once per move line for lot valuated products, with the quantity and value of the lot
- when core estimates a FIFO price without valuing a move (e.g. COGS of an invoice
  without stock moves, PoS), with `valued_move` set to `None`: check it before storing
  anything

The quantity valued beyond the available candidates (negative stock) does not call the
hook. When a later receipt fills that shortage, the FIFO replay calls the hook with the
receipt as candidate.

## FIFO replay

Before replaying the FIFO valuation, `_correct_inventory_valuation()` calls
`_run_fifo_correction_reset(valued_moves)` with the outgoing moves whose value is
recomputed. Override it to drop the data stored for those moves: the replay calls
`_run_fifo_prepare_candidate_update()` again for each of them.
