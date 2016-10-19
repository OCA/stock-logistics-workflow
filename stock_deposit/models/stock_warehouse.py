# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    def _create_deposit_location(self):
        stock_location_obj = self.env['stock.location']
        self.ensure_one()
        stock_location_obj.create({
            'location_id': self.lot_stock_id.id,
            'name': _('Deposit Location'),
            'deposit_location': True,
        })

    def _create_deposit_sequence(self, return_type=False):
        seq_obj = self.env['ir.sequence']
        self.ensure_one()
        dep_seq_id = seq_obj.create({
            'name': self.name + _(
                ' Sequence deposit %s') % ('in' if return_type else 'out'),
            'prefix':
                self.code + '/DEP/%s/' % ('IN' if return_type else 'OUT'),
            'padding': 5,
        })
        return dep_seq_id

    def _get_color(self):
        self.ensure_one()
        wh_color = self.env['stock.picking.type'].search([
            ('warehouse_id', '=', self.id)
        ])[:1].color
        return wh_color

    def _get_sequence(self):
        picking_types = self.env['stock.picking.type'].search([])
        max_sequence = picking_types.sorted(
            key=lambda x: x.sequence, reverse=True)
        max_sequence = max_sequence and max_sequence[:1].sequence or 0
        return max_sequence + 1

    def _prepare_deposit_picking_type_return_values(self):
        child_loc = self.lot_stock_id.child_ids
        res = {
            'name': _('Deposit In'),
            'color': self._get_color(),
            'sequence': self._get_sequence(),
            'sequence_id': self._create_deposit_sequence(return_type=True).id,
            'default_location_src_id': child_loc.filtered(
                'deposit_location')[:1].id,
            'default_location_dest_id': self.lot_stock_id.id,
            'code': 'internal',
            'warehouse_id': self.id,
        }
        return res

    def _prepare_deposit_picking_type_values(self, picking_type_return=None):
        child_loc = self.lot_stock_id.child_ids
        res = {
            'name': _('Deposit Out'),
            'color': self._get_color(),
            'sequence': self._get_sequence(),
            'sequence_id': self._create_deposit_sequence().id,
            'default_location_src_id': self.lot_stock_id.id,
            'default_location_dest_id': child_loc.filtered(
                'deposit_location')[:1].id,
            'code': 'internal',
            'warehouse_id': self.id,
            'return_picking_type_id': picking_type_return.id or False,
        }
        return res

    def _create_deposit_values(self):
        self._create_deposit_location()
        PickingType = self.env['stock.picking.type']
        vals_return = self._prepare_deposit_picking_type_return_values()
        picking_type_return = PickingType.create(vals_return)
        vals = self._prepare_deposit_picking_type_values(picking_type_return)
        PickingType.create(vals)

    @api.model
    def create(self, vals):
        warehouse = super(StockWarehouse, self).create(vals)
        warehouse._create_deposit_values()
        return warehouse
