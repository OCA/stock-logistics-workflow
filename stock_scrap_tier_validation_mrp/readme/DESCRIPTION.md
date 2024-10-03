This module fixes compatibility between `stock_scrap_tier_validation` and the
`mrp` module from Odoo. When scrapping products directly from the production
order form, the scrap record will open in the main window rather than in a
popup form.

This solves a technical issue with the validation flow: it is only
after saving a record that validation can be requested, whereas in the case
of a popup window the record is only saved when closing the window. If
validation is required, this attempt to save the record will raise an exception.
