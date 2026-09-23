This module allows to split a stock move line into smaller move lines. It adds
a Split button in Detailed Operations where users can split quantities either
by a fixed number per line or by maximum weight per line. For weight-based
splitting, the module calculates how many whole product units fit within a weight
limit (custom or based on package type).

All resulting lines stay on the same stock move and preserve relevant data such
as reservations, locations, lots... so the picking remains valid.
