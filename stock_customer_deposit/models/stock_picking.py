# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model_create_multi
    def create(self, vals_list):
        pickings = super().create(vals_list)
        for picking in pickings.filtered(lambda p: p.picking_type_id.assign_owner):
            picking.write(
                {
                    "location_dest_id": picking.picking_type_id.default_location_dest_id,
                }
            )
        return pickings

    def button_validate(self):
        if self.picking_type_id.assign_owner:
            return super(
                StockPicking,
                self.with_context(
                    owner=self.partner_id.commercial_partner_id.id or self.partner_id.id
                ),
            ).button_validate()
        return super(StockPicking, self).button_validate()
