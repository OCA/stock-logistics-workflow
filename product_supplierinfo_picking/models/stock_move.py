# Copyright 2020 ForgeFlow S.L.
#     (<https://www.forgeflow.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    @api.depends('picking_id.partner_id', 'product_id',
                 'product_id.seller_ids.product_code')
    def _compute_product_supplier_code(self):
        for move in self.filtered(lambda m: m.picking_id and
                                  m.picking_id.partner_id and
                                  m.product_tmpl_id.seller_ids):
            suppliers = \
                move.product_tmpl_id.seller_ids.filtered(
                    lambda m: m.name == move.picking_id.partner_id)
            if suppliers:
                move.product_supplier_name = suppliers[0].product_name
                move.product_supplier_code = suppliers[0].product_code

    product_supplier_name = fields.Char(
        compute='_compute_product_supplier_code',
        string='Product Supplier Name',
        store=True,
        size=64
    )
    product_supplier_code = fields.Char(
        compute='_compute_product_supplier_code',
        string='Product Supplier Code',
        store=True,
        size=64
    )
