In Odoo quants are used for a quick overview of stock levels, that are based on
stock moves, or rather stock move lines ('Detailed operations'). In previous
versions of Odoo measures like Quantity On Hand (QOH) of Quantity Available were
always computed on stock moves since the beginning of time, which caused hideously
bad performance.

With stock quants performance improved immensely, but is also lead to redundancy in
the database, and therefore inconsistency.

This module will provide methods to report on inconsistencies, and where possible to
repair them.

The information from the stock moves (and lines) will be considered 'The Truth'.
Quants will have to confirm to these.
