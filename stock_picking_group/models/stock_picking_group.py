# Copyright 2021 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPickingGroup(models.Model):
    _name = 'stock.picking.group'

    name = fields.Char(string='Group Reference')
    picking_ids = fields.Many2many(
        comodel_name='stock.picking', inverse_name='picking_group_id',
        string='Pickings')
    has_serial_number = fields.Boolean(
        compute='_get_has_serial_number', string='Has Serial Number')
    remaining = fields.Boolean(
        compute='_get_remaining', string='Remaining')
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner')

    def _get_has_serial_number(self):
        has_serial_number = False
        for picking in self.picking_ids:
            if picking.state == 'done':
                for move in picking.move_line_ids:
                    if move.lot_id:
                        has_serial_number = True
                        break
            if has_serial_number:
                break
        self.has_serial_number = has_serial_number

    def _get_remaining(self):
        remaining = False
        for picking in self.picking_ids:
            for backorder in picking.backorder_ids:
                if backorder.state not in ('done', 'cancel'):
                    remaining = True
                    break
            if remaining:
                break
        self.remaining = remaining

    @api.model
    def create(self, vals):
        sequence_obj = self.env['ir.sequence']
        new_group = super(StockPickingGroup, self).create(vals)
        # Verify that all picking_ids have the same partner_id and carrier_id
        company_id = new_group.picking_ids[0].company_id.id
        partner_id = new_group.picking_ids[0].partner_id.id
        for picking in new_group.picking_ids:
            if partner_id != picking.partner_id.id:
                raise UserError(
                    _('Grouped pickings must have same parnter.'))
            picking.picking_group_id = new_group
        new_group.name = sequence_obj.with_context(force_company=company_id).\
            next_by_code('stock.picking.group') or _('New')
        new_group.partner_id = partner_id
        return new_group

    @api.multi
    def write(self, vals):
        res = super(StockPickingGroup, self).write(vals)
        # Verify that all picking_ids have the same partner_id and carrier_id
        if 'picking_ids' in vals:
            for group in self:
                if group.picking_ids:
                    partner_id = group.picking_ids[0].partner_id.id
                    for picking in group.picking_ids:
                        if partner_id != picking.partner_id.id:
                            raise UserError(
                                _('Grouped pickings must have same parnter.'))
                        picking.picking_group_id = group
        return res
