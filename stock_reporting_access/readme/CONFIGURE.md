To configure this module, you need to:

1. Go to Settings > Users & Companies > Groups
2. Search for "Inventory Reporting Access"
3. Add users who should have access to inventory reporting to this group

The ``stock.valuation.layer`` model is restricted to Inventory Managers by default.
If ``stock_account`` is installed, the access rights for ``stock.valuation.layer``
should be added manually as necessary:

1. Go to Settings > Technical > Models
2. Search for ``stock.valuation.layer``
3. Open the model and go to the Access Rights tab
4. Add read-only permission for the "Inventory Reporting Access" group
