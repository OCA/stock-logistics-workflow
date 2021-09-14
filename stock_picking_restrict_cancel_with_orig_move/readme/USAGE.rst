Odoo allows to cancel any picking in a chain of moves between locations, and
will automatically cancel the ensuing moves but leaves the previous ones in
their actual state.

This module restricts this possibility and displays an error to the user,
listing all the stock pickings containing stock moves linked to the picking the
user is trying to cancel, so he can delete the original, ensuring all the
following pickings will be canceled as well.
