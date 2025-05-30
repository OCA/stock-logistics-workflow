When reserving stock on the delivery note that has activated the `reserve_max_quantity` flag,
if you reserve stock and it matches exactly the initially demanded quantity, it will stop reserving.

Example:
Pick: 2 units requested, 3 units made in 3 different move lines. (1 + 1 + 1)
Ship: 2 units requested. Stock will only be taken until the 2 units are reached. (1 + 1)

This happens because there comes a time when the demand to cover the initial need is 0, and the line of 1 unit will be left untaken because all has been satisfied.
