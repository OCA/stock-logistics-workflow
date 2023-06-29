This module adds to the lot model the unit price field, which takes the value from the
corresponding field of the stock move that has created the lot.

The unit price of the lot is just for reference only. It does not reflect miscellaneous
adjustments (e.g. variances between the receipt price and the vendor bill price, landed
costs, etc.) that are reflected in the stock valuation layer.

Background
~~~~~~~~~~

People on the shopfloor sometimes want to know the "real" unit price of the inventory
they are going to consume or sell, according to the purchase costs. Having this
information on the lot can be helpful even if it is not 100% accurate.
