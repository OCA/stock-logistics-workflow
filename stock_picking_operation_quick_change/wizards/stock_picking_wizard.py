# -*- coding: utf-8 -*-
# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPickingOperationWizard(models.TransientModel):
    _name = 'stock.picking.operation.wizard'

    def _prepare_default_values(self, picking):
        return {'location_dest_id': picking.location_dest_id.id}

    @api.model
    def default_get(self, fields):
        res = super(StockPickingOperationWizard, self).default_get(fields)
        active_model = self.env.context['active_model']
        active_ids = self.env.context['active_ids'] or []
        picking = self.env[active_model].browse(active_ids)
        res.update(self._prepare_default_values(picking))
        return res

    def _default_old_dest_location_id(self):
        stock_picking_obj = self.env['stock.picking']
        pickings = stock_picking_obj.browse(self.env.context['active_ids'])
        first_operation = pickings.mapped('pack_operation_product_ids')[:1]
        return first_operation.location_dest_id.id

    def _get_allowed_locations(self):
        return ['internal']

    def _get_allowed_location_domain(self):
        return [('usage', 'in', self._get_allowed_locations())]

    def _get_allowed_picking_states(self):
        return ['assigned']

    location_dest_id = fields.Many2one(
        comodel_name='stock.location',
        string='Actual destination location',
        required=True,
        readonly=True,
    )
    old_location_dest_id = fields.Many2one(
        comodel_name='stock.location',
        string='Old destination location',
        default=_default_old_dest_location_id,
        domain=lambda self: self._get_allowed_location_domain(),
    )
    new_location_dest_id = fields.Many2one(
        comodel_name='stock.location',
        string='New destination location',
        required=True,
        domain=lambda self: self._get_allowed_location_domain(),
    )
    change_all = fields.Boolean(
        string='Change All',
        help='Check if you want change all operations without filter '
             'by old location')

    def check_forbbiden_pickings(self, pickings):
        forbidden_pickings = pickings.filtered(
            lambda x: x.state not in self._get_allowed_picking_states())
        if forbidden_pickings:
            raise UserError(_(
                'You can not change operations destination location if '
                'picking state not is in %s') % ','.join(
                self._get_allowed_picking_states()))
        pikings_with_chained_moves = pickings.filtered(
            lambda x: x.move_lines.mapped('move_dest_id'))
        if pikings_with_chained_moves:
            raise UserError(_(
                'You cannot change destination location if any move has a '
                'destination move.'))

    @api.multi
    def action_apply(self):
        stock_picking_obj = self.env['stock.picking']
        pickings = stock_picking_obj.browse(self.env.context['active_ids'])
        self.check_forbbiden_pickings(pickings)
        operations = pickings.mapped('pack_operation_product_ids')

        vals = {'location_dest_id': self.new_location_dest_id.id}
        if self.change_all:
            # Write all operations destination location
            operations.write(vals)
        else:
            # Only write operations destination location if the location is
            # the same that old location value
            matched_op = operations.filtered(
                lambda x: x.location_dest_id == self.old_location_dest_id)
            matched_op.write(vals)
        return {'type': 'ir.actions.act_window_close'}
