By default Odoo doesn't enforce any limit on item quantity that can be returned in picking. It means that it is possible to return more items that there were in the original picking.
Eg if you delivered 5 pcs of "Acoustic Block Screens" in picking you can return 8 pcs of it.
This module implements constraint with allows to return not more than the original amount of item in the picking. It also takes into account existing returns for the same picking.
Eg if you delivered 5 pcs of "Acoustic Block Screens" in picking then you can return no more than 5 pcs of it. If you have already returned 2 pcs in the same picking then you can return no more than 3 pcs.
