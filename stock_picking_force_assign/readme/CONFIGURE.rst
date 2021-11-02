By default, the forced reservation is rolled back if the picking to reserve
cannot be satisfied fully, and the user is presented with a warning message.
To allow partial forced reservation, change the value of the system setting
`stock_picking_force_assign.allow_partial` to `True`. This entails that no
message is displayed when no assignment, or only a partial assignment was
possible.
