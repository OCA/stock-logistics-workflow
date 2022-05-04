from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    available_lot_ids = fields.Many2many(
        'stock.production.lot',
        compute='_compute_available_lot_ids'
    )

    @api.depends('product_id')
    def _compute_available_lot_ids(self):
        for line in self:
            domain = [('product_id', '=', line.product_id.id)]
            if line.picking_id.picking_type_id.use_location_lots:
                domain.extend([('location_ids', 'child_of', line.location_id.id)])
            if line.picking_id.picking_type_id.use_available_lots:
                domain.extend([('product_qty', '>', 0)])
            line.available_lot_ids = self.env['stock.production.lot'].search(domain).ids
