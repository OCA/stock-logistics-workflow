# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    pack_weight = fields.Float('Weight (kg)')
    # length cannot be used in onchange: https://github.com/odoo/odoo/issues/41353
    length_alt = fields.Integer('Length (mm)', help='length in millimeters')
    width = fields.Integer('Width (mm)', help='width in millimeters')
    height = fields.Integer('Height (mm)', help='height in millimeters')
    volume = fields.Float(
        'Volume (m³)',
        digits=(8, 4),
        compute='_compute_volume',
        readonly=True,
        store=False,
        help='volume in cubic meters',
    )

    @api.depends('length_alt', 'width', 'height')
    def _compute_volume(self):
        for pack in self:
            pack.volume = (
                pack.length_alt * pack.width * pack.height
            ) / 1000.0 ** 3

    def auto_assign_packaging(self):
        self = self.with_context(_auto_assign_packaging=True)
        res = super().auto_assign_packaging()
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if (
            self.env.context.get('_auto_assign_packaging')
            and vals.get('product_packaging_id')
        ):
            for package in self:
                package.onchange_product_packaging_id()
        return res

    @api.onchange('product_packaging_id')
    def onchange_product_packaging_id(self):
        if self.product_packaging_id:
            vals = self.product_packaging_id.read(
                fields=['length', 'width', 'height', 'max_weight']
            )[0]
            vals['pack_weight'] = vals['max_weight']
            vals.pop('id')
            vals.pop('max_weight')
            self.update(vals)
