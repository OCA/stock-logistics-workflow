# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from datetime import timedelta

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.depends("product_id", "picking_type_use_create_lots", "lot_id.expiration_date")
    def _compute_expiration_date(self):
        expiration_dtt_move_line_map = {}
        for move_line in self:
            if move_line.lot_id.expiration_date:
                continue
            if not move_line.picking_type_use_create_lots:
                continue
            if not move_line.product_id.use_expiration_date:
                continue
            if move_line.expiration_date:
                continue
            # will be managed by super() until here
            expiration_dtt = False
            if move_line.product_id.expiration_time > 0:
                expiration_dtt = fields.Datetime.today() + timedelta(
                    days=move_line.product_id.expiration_time
                )
            expiration_dtt_move_line_map.setdefault(move_line, expiration_dtt)
        # super writes the expiration date if it's filled directly from Stock Move
        res = super()._compute_expiration_date()
        # apply expiration date calculated before super
        for move_line in self.filtered(lambda ml: ml in expiration_dtt_move_line_map):
            move_line.expiration_date = expiration_dtt_move_line_map[move_line]
        return res

    @api.onchange("product_id", "product_uom_id")
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        if not self.picking_type_use_create_lots:
            return res
        if not self.product_id.use_expiration_date:
            return res
        # managed by super() until here
        expiration_dtt = False
        if self.product_id.expiration_time > 0:
            expiration_dtt = fields.Datetime.today() + timedelta(
                days=self.product_id.expiration_time
            )
        self.expiration_date = expiration_dtt
        return res
