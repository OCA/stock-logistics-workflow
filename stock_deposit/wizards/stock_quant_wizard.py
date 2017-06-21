# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models
from openerp.exceptions import UserError, ValidationError


class StockQuantWizard(models.TransientModel):
    _name = 'deposit.stock.quant.wizard'

    @api.model
    def default_get(self, fields_list):
        res = super(StockQuantWizard, self).default_get(fields_list)
        quant_ids = self.env.context.get('active_ids', False)
        if quant_ids:
            quants = self.env['stock.quant'].browse(quant_ids)
            res['line_ids'] = [(0, 0, {
                'quant_id': x.id,
                'product_id': x.product_id.id,
                'location_id': x.location_id.id,
                'owner_id': x.owner_id.id,
                'new_qty': x.qty,
            }) for x in quants]
        return res

    def _default_old_dest_location_id(self):
        stock_picking_obj = self.env['stock.picking']
        pickings = stock_picking_obj.browse(self.env.context['active_ids'])
        first_operation = pickings.mapped('pack_operation_product_ids')[:1]
        return first_operation.location_dest_id.id

    quants_action = fields.Selection([
        ('regularize', 'Regularize')
    ], string='Quants Action', default='regularize')
    line_ids = fields.One2many(
        comodel_name='deposit.stock.quant.wizard.line',
        inverse_name='stock_quant_wizard_id',
    )

    def check_forbbiden_quants(self, quants):
        forbidden_quants = quants.filtered(
            lambda x: not x.location_id.deposit_location)
        if forbidden_quants:
            raise UserError(_('You can not regularize quants in a non deposit '
                              'location'))

    def _get_picking_type_out(self, wharehouse_id):
        picking_type = self.env['stock.picking.type'].search([
            ('warehouse_id', '=', wharehouse_id),
            ('code', '=', 'outgoing'),
        ])[:1]
        return picking_type.id

    def _prepare_product_quant(self, quant):
        return {
            'name': quant.product_id.name,
            'product_id': quant.product_id.id,
            'product_uom_qty': quant.new_qty,
            'product_uom': quant.product_id.uom_id.id,
            'restrict_partner_id': quant.owner_id.id,
        }

    def _get_regularize_sequence(self):
        ir_sequence_obj = self.env['ir.sequence']
        return ir_sequence_obj.next_by_code(
            'stock.deposit.regularize.sequence')

    def _prepare_picking(self, location, owner, quants):
        # For test purpose.
        warehouse = self.env.context.get(
            'warehouse', location.get_warehouse(location))
        vals = {
            'name': self._get_regularize_sequence(),
            'origin': _('Deposit %s') % ','.join(str(x.id) for x in quants),
            'partner_id': owner.id,
            'owner_id': owner.id,
            'location_id': location.id,
            'location_dest_id': owner.property_stock_customer.id,
            'picking_type_id':
                self._get_picking_type_out(warehouse),
            'move_lines': [(0, 0,
                            self._prepare_product_quant(x)) for x in quants],
        }
        return vals

    def _validate_pickings(self, picking_ids):
        # Validate all pickings
        picking_obj = self.env['stock.picking']
        pickings = picking_obj.browse(picking_ids)
        pickings.action_assign()
        pickings_not_assigned = pickings.filtered(
            lambda x: x.state != 'assigned')
        if pickings_not_assigned:
            raise UserError(
                _("Could not reserve all requested products. "
                  "Please you must handle the reservation manually."))
        pickings.do_transfer()

    def _regularize_quants(self):
        picking_obj = self.env['stock.picking']
        quants = self.line_ids.filtered(lambda q: q.new_qty > 0)
        self.check_forbbiden_quants(quants)
        # Make new stock picking by each stock quant location
        new_picking_ids = []
        for location in quants.mapped('location_id'):
            loc_quants = quants.filtered(lambda x: x.location_id == location)
            for owner in loc_quants.mapped('owner_id'):
                owner_quants = loc_quants.filtered(
                    lambda x: x.owner_id == owner)
                picking = picking_obj.create(
                    self._prepare_picking(location, owner, owner_quants))
                new_picking_ids.append(picking.id)
        self._validate_pickings(new_picking_ids)
        return new_picking_ids

    @api.multi
    def action_apply(self):
        if self.quants_action == 'regularize':
            return self._regularize_quants()
        return False


class StockQuantWizardLine(models.TransientModel):
    _name = 'deposit.stock.quant.wizard.line'

    stock_quant_wizard_id = fields.Many2one(
        comodel_name='deposit.stock.quant.wizard',
    )
    quant_id = fields.Many2one(
        comodel_name='stock.quant',
        readonly=True,
        string='Quant',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        readonly=True,
        string='Product',
    )
    location_id = fields.Many2one(
        comodel_name='stock.location',
        readonly=True,
        string='Location',
    )
    owner_id = fields.Many2one(
        comodel_name='res.partner',
        readonly=True,
        string='Owner',
    )
    new_qty = fields.Float(string='Qty to process')

    @api.multi
    @api.constrains('new_qty')
    def _check_new_qty(self):
        if self.filtered(lambda x: x.new_qty > x.quant_id.qty):
            raise ValidationError(
                _('There is any line with new quantity greater than quant '
                  'quantity.\n'
                  'Please, fix it before continuing'))
