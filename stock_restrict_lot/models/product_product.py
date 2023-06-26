# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # To be able to get the outgoing and incoming qty by the restrict_lot_id
    # the odoo standard method _compute_quantities_dict is hookable
    # therefore the domain is already here changed
    def _get_domain_locations(self):
        res = super()._get_domain_locations()
        lot_id = self.env.context.get("lot_id")
        if not lot_id:
            return res

        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = res
        lot_domain = [("restrict_lot_id", "=", lot_id)]
        domain_move_in_loc += lot_domain
        domain_move_out_loc += lot_domain
        return domain_quant_loc, domain_move_in_loc, domain_move_out_loc
