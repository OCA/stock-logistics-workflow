# Copyright 2019 Kitti U. - Ecosoft <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    product_kit_helper_ids = fields.One2many(
        comodel_name='stock.picking.product.kit.helper',
        string='Product Kit Helper Lines',
        inverse_name='picking_id',
        readonly=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
    )
    has_product_kit = fields.Boolean(
        string='Has Product Kit',
        compute='_compute_has_product_kit',
        default=False,
        help="True if there is at least 1 product kit in the sales order",
    )

    @api.model
    def _is_product_kit(self, product, company):
        BOM = self.env['mrp.bom'].sudo()
        bom = BOM._bom_find(product=product,
                            company_id=company.id)
        return bom and bom.type == 'phantom'

    @api.one
    def _compute_has_product_kit(self):
        # self.has_product_kit = False
        for sale_line in self.move_lines.mapped('sale_line_id'):
            is_kit = self._is_product_kit(sale_line.product_id,
                                          sale_line.company_id)
            if is_kit:
                self.has_product_kit = True
                break

    @api.multi
    def show_product_kit(self):
        """Find move_lines with product kit to create helper line."""
        self.ensure_one()
        BOM = self.env['mrp.bom'].sudo()
        helpers = []
        for sale_line in self.move_lines.mapped('sale_line_id'):
            bom = BOM._bom_find(product=sale_line.product_id,
                                company_id=sale_line.company_id.id)
            if bom and bom.type == 'phantom':  # Create product kit line
                helpers.append((0, 0, {'sale_line_id': sale_line.id,
                                       'product_id': sale_line.product_id.id,
                                       'product_uom_qty': 0.0,
                                       }))
        self.product_kit_helper_ids.unlink()
        self.write({'product_kit_helper_ids': helpers})

    @api.multi
    def action_product_kit_helper(self):
        """Assign product kit's quantity to stock move."""
        self.ensure_one()
        if self.state in ('done', 'cancel'):
            raise ValidationError(
                _('Product Kit Helper is not allowed on current state'))
        for helper in self.product_kit_helper_ids:
            helper.action_explode_helper()


class StockPickingProductKitHelper(models.Model):
    _name = 'stock.picking.product.kit.helper'
    _description = """
        Product Kit Helper, allow user to specify quantity of product kit,
        to explode as product quantity in operations tab
    """

    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Picking',
        required=True,
        index=True,
    )
    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sales Order Line',
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
        readonly=True,
    )
    product_uom_qty = fields.Float(
        string='Quantity',
    )
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
        related='sale_line_id.product_uom',
        readonly=True,
    )

    @api.multi
    def action_explode_helper(self):
        """Explodes product kit quantity to detailed product in stock move."""
        self.ensure_one()
        # Mock stock.move, in order to resue stock.move's action_explode
        StockMove = self.env['stock.move']
        mock_loc = self.env['stock.location'].sudo().search([], limit=1)
        mock_pt = self.env['stock.picking.type'].sudo().search([], limit=1)
        mock_stock_move = StockMove.sudo().create({
            'name': '/',
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': self.product_uom_qty,
            'picking_type_id': mock_pt.id,
            'location_id': mock_loc.id,
            'location_dest_id': mock_loc.id,
        })
        # Reuse explode function and assign quantity_done in stock.move
        mock_processed_moves = mock_stock_move.action_explode()
        for mock_move in mock_processed_moves:
            stock_move = StockMove.search([
                ('picking_id', '=', self.picking_id.id),
                ('sale_line_id', '=', self.sale_line_id.id),
                ('product_id', '=', mock_move.product_id.id)])
            if len(stock_move) != 1:
                raise ValidationError(
                    _('No matching detailed product %s for product kit %s') %
                    (mock_move.product_id.display_name,
                     self.product_id.display_name))
            stock_move.write({'quantity_done': mock_move.product_uom_qty})
        mock_processed_moves.sudo().unlink()
