# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.fields import Domain


class ProductProduct(models.Model):
    _inherit = "product.product"

    # To be able to get the outgoing and incoming qty by the restrict_lot_id
    # _get_domain_locations injects restrict_lot_id into the move location domains.
    # _compute_quantities_dict passes lot_id=None to super() so that the standard
    # move_line_ids.lot_id filter is not added (it would exclude pending moves with
    # no move lines yet); our _get_domain_locations() handles the filtering instead.
    def _get_domain_locations(self):
        res = super()._get_domain_locations()
        lot_id = self.env.context.get("lot_id")
        if not lot_id:
            return res
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = res
        lot_domain = Domain("restrict_lot_id", "=", lot_id)
        domain_move_in_loc = domain_move_in_loc & lot_domain
        domain_move_out_loc = domain_move_out_loc & lot_domain
        return domain_quant_loc, domain_move_in_loc, domain_move_out_loc
