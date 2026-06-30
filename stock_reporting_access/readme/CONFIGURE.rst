To configure this module, you need to:

#. Go to *Settings > Users & Companies > Groups*
#. Search for "Inventory Reporting Access"
#. Add users who should have access to inventory reporting to this group

The ``stock.valuation.layer`` model is restricted to Inventory Managers by
default. If ``stock_account`` is installed, the access rights for
``stock.valuation.layer`` should be added manually as necessary:

#. Go to *Settings > Technical > Models*
#. Search for ``stock.valuation.layer``
#. Open the model and go to the Access Rights tab
#. Add read-only permission for the "Inventory Reporting Access" group
