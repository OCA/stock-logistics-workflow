from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("picking_type_id"):
                picking_type = self.env["stock.picking.type"].browse(
                    vals["picking_type_id"]
                )
                if picking_type.default_move_type:
                    vals["move_type"] = picking_type.default_move_type
        return super().create(vals_list)
