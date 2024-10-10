This module adds a field on stock picking that will check if all movements have
been filled in by stock operator.

This is helpful to see if at least all lines of the picking have been treated.
The picking would not be marked as ready if some quantities stay at 0 (backorders) and
quantities are < the reserved one.
