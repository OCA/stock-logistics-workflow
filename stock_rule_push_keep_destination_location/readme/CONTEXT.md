When Odoo apply a push rule destination, it relies on move's final location
to check if it is not a child of the push rule destination.

Either, it keeps the move's final location for the generated move (from the push rule).

This is not convenient in some cases:

- When Input location is under Stock one (we want to take into account quantities early)
- When we have putaways on Stock location.
