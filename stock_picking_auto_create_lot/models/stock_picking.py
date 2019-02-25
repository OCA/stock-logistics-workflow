# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    auto_create_lot = fields.Boolean(string='Auto Create Lot')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        if self.picking_type_id.auto_create_lot:
            for line in self.move_line_ids.filtered(lambda x: (
                    not x.lot_id and not x.lot_name and
                    x.product_id.tracking != 'none' and
                    x.product_id.auto_create_lot)):
                line.lot_id = self.env['stock.production.lot'].create({
                    'product_id': line.product_id.id,
                })
        return super().button_validate()
