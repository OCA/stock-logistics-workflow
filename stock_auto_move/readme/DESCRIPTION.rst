This modules adds the possibility to have move automatically processed as soon
as the products are available in the move source location.

It also adds the possibility to define the move as being automatic in
a procurement rule.

Automatic moves are triggered by previous move when the move is chained
or by the scheduler otherwise.

Note that automatic moves are given a procurement group name "Automatic",
whatever the user or the procurement rule selects.

It's different than the standard 'Automatic No step added' option in stock
rules as it does not merge first and second chained move.
