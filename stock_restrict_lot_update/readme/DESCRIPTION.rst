This module builds on `stock_restrict_lot` and exposes the field
`restrict_lot_id` of `stock.move`, allowing the user to update or
even remove the lot restriction if the product does not fall within
a domain.

The domain can be updated in the settings of each individual company.

Any change to `restrict_lot_id` is propagated to linked stock moves,
but only forwards, not backwards.
