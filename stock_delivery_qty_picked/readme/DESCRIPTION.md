Glue module between `stock_delivery` and `stock_move_line_qty_picked`.

When installed, the shipping weight computed in the "Put in Pack" wizard
(`choose.delivery.package`) and the per-package weight returned by
`stock.quant.package._get_weight` use the picked quantity of each move line
instead of its reserved quantity. Specifically:

- Shipping weight computed in the Put in Pack wizard.
- Per-package weight for a given picking.
- Bulk weight on the picking which is sent as the bulk parcel weight.
