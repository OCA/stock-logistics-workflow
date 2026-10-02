# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.tools import float_compare


class ChooseDeliveryPackage(models.TransientModel):
    _inherit = "choose.delivery.package"

    @api.depends("delivery_package_type_id")
    def _compute_shipping_weight(self):
        res = super()._compute_shipping_weight()
        for rec in self:
            move_line_ids = rec.picking_id._package_move_lines(
                batch_pack=self.env.context.get("batch_pack")
            )
            if sml_ids := self.env.context.get("selected_smls_to_pack", False):
                move_line_ids = self.env["stock.move.line"].browse(sml_ids)
            weight_adjustment = 0.0
            for ml in move_line_ids:
                if (
                    ml.picked
                    and float_compare(
                        ml.qty_picked,
                        ml.quantity,
                        precision_rounding=ml.product_uom_id.rounding,
                    )
                    != 0
                ):
                    orig_qty = ml.product_uom_id._compute_quantity(
                        ml.quantity, ml.product_id.uom_id
                    )
                    actual_qty = ml.product_uom_id._compute_quantity(
                        ml.qty_picked, ml.product_id.uom_id
                    )
                    weight_adjustment += (actual_qty - orig_qty) * ml.product_id.weight
            rec.shipping_weight += weight_adjustment
        return res
