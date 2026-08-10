* A product-wide revaluation of a lot tracked FIFO product is spread over the
  lots in proportion to their remaining quantity. This is consistent with what
  Odoo does to the valuation layers, but it is a quantity weighted spread, not a
  per-lot judgement; use the lot revaluation of ``stock_valuation_fifo_lot``
  instead when the value belongs to a specific lot.
* Applying a landed cost to a receipt after the lot has been revalued is
  outside the scope of ``stock_valuation_fifo_lot``, and remains so here.
