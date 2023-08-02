By default Odoo doesn't enforce any limit quantity of items that can be retuned in picking. It means that it is possible to return more items that there were in the original picking.

Eg if you delivered 5 pcs of "Acoustic Bloc Screens" in picking you can return 8 pcs of it.

This module implements constraint with allows to return not more than the original amount of item in the picking. It also takes into account existing returns for the same picking.

If user tries to return more items than it is possible to return following blocking messages is shown: "You can return only <X> of <product_name>"

Eg if you delivered 5 pcs of "Acoustic Bloc Screens" in picking you can return no more than 5 pcs of it. If you have already returned 2 pcs then you can return no more than 3 pcs.
