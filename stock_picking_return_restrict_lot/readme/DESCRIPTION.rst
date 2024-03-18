This module create a full return picking that restrict lots to be used.

The Odoo return wizard let user choose quantity per stock move before generating
the return's picking. Existing source code is quite hard to overwrite to choose specific
quantity per lot.

So this module prepare a full return based on what have been moved and let user
to choose quantities to returns or not (user is able to do a partial picking an do
not create backorder), based on `stock_restrict_lot` module this allow to prepare
return picking restricting quantities per lot and final locations.


.. note::

    Be aware, while returning quantities from a return picking generate by this
    module, chains moved that were not processed will be unreserved waiting availability.
    (same behaviour like odoo while using the return wizard)
