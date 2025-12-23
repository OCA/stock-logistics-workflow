# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model_create_multi
    def create(self, vals):
        if self.env.company.carrier_auto_assign_picking:
            ResPartner = self.env["res.partner"]
            PickingType = self.env["stock.picking.type"]
            for val in vals:
                if "picking_type_id" in val and "partner_id" in val:
                    partner_id = ResPartner.browse(val["partner_id"])
                    picking_type_id = PickingType.browse(val["picking_type_id"])
                    if picking_type_id.carrier_auto_assign_picking:
                        val["carrier_id"] = (
                            partner_id.parent_id.property_delivery_carrier_id.id
                            or partner_id.property_delivery_carrier_id.id
                        )
        return super().create(vals)

    @api.onchange("partner_id", "picking_type_id")
    def _onchange_partner_id(self):
        if self.env.company.carrier_auto_assign_picking:
            for picking in self:
                if picking.picking_type_id.carrier_auto_assign_picking:
                    partner_id = picking.partner_id
                    picking.carrier_id = (
                        partner_id.parent_id.property_delivery_carrier_id.id
                        or partner_id.property_delivery_carrier_id.id
                    )
