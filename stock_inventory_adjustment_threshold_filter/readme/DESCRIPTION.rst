This module helps validating a large number of pending stock inventory
adjustments at once, based on their adjustment cost and quantity
difference, instead of applying them one by one or through the standard
(and not very ergonomic) search filters.

It adds:

* A dedicated "Inventory Adjustments (Threshold Filter)" menu (a variant of the
  standard "Inventory Adjustments" screen, filtered on "To Apply" by
  default) with a search panel to narrow down the quants by adjustment
  cost threshold, quantity difference threshold, and whether the
  adjustment is positive, negative, and/or exactly zero (no
  difference). Each threshold can be used as a lower or an upper bound,
  to either spot the adjustments that need attention or bulk-process
  the ones that don't.
* Configurable default cost / quantity difference thresholds (company
  level), proposed on the search panel.

This relies entirely on Odoo's standard selection and bulk "Apply"
button (which prompts for an inventory adjustment name/reference) -
the search panel only makes it comfortable to narrow down the quants
to select, including selecting every quant matching the search beyond
the current page.

This module depends on `stock_quant_cost_info
<https://github.com/OCA/stock-logistics-warehouse>`_ for the adjustment
cost information.
