# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round, float_compare


class StockPickingScrapLine(models.TransientModel):
    _name = "wiz.stock.picking.scrap.line"
    _rec_name = 'product_id'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        readonly=True,
    )
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lot',
        readonly=True,
    )
    package_id = fields.Many2one(
        comodel_name='stock.quant.package',
        string='Package',
        readonly=True,
    )
    owner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Owner',
        readonly=True,
    )
    quantity = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        required=True,
    )
    uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='Unit of Measure',
        readonly=True,
    )
    wizard_id = fields.Many2one(
        comodel_name='wiz.stock.picking.scrap',
        string='Wizard',
    )
    move_line_id = fields.Many2one(
        comodel_name='stock.move.line',
        string='Move Line',
    )


class StockPickingScrap(models.TransientModel):
    _name = 'wiz.stock.picking.scrap'
    _description = 'Picking Whole Scrap'

    picking_id = fields.Many2one(comodel_name='stock.picking')
    line_ids = fields.One2many(
        comodel_name='wiz.stock.picking.scrap.line',
        inverse_name='wizard_id',
        string='Moves',
    )
    scrap_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Scrap Location',
        domain=[('scrap_location', '=', True)],
    )

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError("You may only return one picking at a time!")
        res = super().default_get(fields)
        scrap_lines = []
        picking = self.env['stock.picking'].browse(
            self.env.context.get('active_id')
        )
        if picking:
            res.update({'picking_id': picking.id})
            if picking.state != 'done':
                raise UserError(_("You may only scrap pickings in done state"))
            for move_line in picking.move_line_ids:
                if move_line.move_id.scrapped:
                    continue
                quantity = move_line.qty_done
                quantity = float_round(
                    quantity,
                    precision_rounding=move_line.product_uom_id.rounding)
                scrap_lines.append((0, 0, {
                    'product_id': move_line.product_id.id,
                    'lot_id': move_line.lot_id.id,
                    'package_id': move_line.package_id.id,
                    'owner_id': move_line.owner_id.id,
                    'quantity': quantity,
                    'uom_id': move_line.product_uom_id.id,
                    'move_line_id': move_line.id,
                }))
            if 'line_ids' in fields:
                res.update({'line_ids': scrap_lines})
            if 'scrap_location_id' in fields:
                scrap_location = self.env['stock.location'].search([
                    ('scrap_location', '=', True),
                ], limit=1)
                res['scrap_location_id'] = scrap_location.id
        return res

    def _prepare_stock_scrap(self, scrap_line):
        vals = {
            'product_id': scrap_line.product_id.id,
            'product_uom_id': scrap_line.uom_id.id,
            'lot_id': scrap_line.move_line_id.lot_id.id,
            'package_id': scrap_line.move_line_id.package_id.id,
            'owner_id': scrap_line.move_line_id.owner_id.id,
            'move_id': scrap_line.move_line_id.move_id.id,
            'picking_id': scrap_line.move_line_id.picking_id.id,
            'location_id': scrap_line.move_line_id.location_dest_id.id,
            'scrap_location_id': self.scrap_location_id.id,
            'scrap_qty': scrap_line.quantity,
        }
        return vals

    def create_scrap(self):
        StockScrap = self.env['stock.scrap']
        new_scraps = StockScrap.browse()
        for line in self.line_ids.filtered('quantity'):
            if float_compare(line.quantity, line.move_line_id.qty_done,
                             precision_rounding=line.uom_id.rounding) > 0:
                raise UserError(
                    _("You can't scrap more quantity that done it"))
            new_scraps += StockScrap.create(self._prepare_stock_scrap(line))
        new_scraps.do_scrap()
        return new_scraps
