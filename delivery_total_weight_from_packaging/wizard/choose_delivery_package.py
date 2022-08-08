# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools.float_utils import float_compare


class ChooseDeliveryPackage(models.TransientModel):

    _inherit = "choose.delivery.package"

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if "shipping_weight" in fields_list:
            picking = self.env["stock.picking"].browse(defaults.get("picking_id"))
            move_line_ids = picking.move_line_ids.filtered(
                lambda m: float_compare(
                    m.qty_done, 0.0, precision_rounding=m.product_uom_id.rounding
                )
                > 0
                and not m.result_package_id
            )
            total_weight = 0.0
            for ml in move_line_ids:
                qty = ml.product_uom_id._compute_quantity(
                    ml.qty_done, ml.product_id.uom_id
                )
                # This is the only line changed from the origin implementation
                total_weight += self._calc_weight_for_move_line(ml, qty)
            defaults["shipping_weight"] = total_weight
        return defaults

    def _calc_weight_for_move_line(self, move_line, qty):
        # Override to compute weight based on packaging
        return move_line.product_id.get_total_weight_from_packaging(qty)
