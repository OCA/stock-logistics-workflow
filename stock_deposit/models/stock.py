# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    deposit_location = fields.Boolean(
        string='Is a Deposit Location?',
        help='Check this box to allow using this location to put deposit '
             'goods.',
    )


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.multi
    @api.depends(
        'default_location_dest_id',
        'default_location_dest_id.deposit_location',
        'default_location_src_id',
        'default_location_src_id.deposit_location',
    )
    def _compute_is_deposit(self):
        for picking_type in self:
            if picking_type.default_location_dest_id.deposit_location or \
                    picking_type.default_location_src_id.deposit_location:
                picking_type.is_deposit = True

    is_deposit = fields.Boolean(
        compute='_compute_is_deposit',
        string='Is a deposit',
        store=True,
    )


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_deposit = fields.Boolean(
        string='Is Deposit',
        related='picking_type_id.is_deposit',
        store=True,
        readonly=True
    )

    @api.model
    def _prepare_pack_ops(self, picking, quants, forced_qties):
        res = super(StockPicking, self)._prepare_pack_ops(
            picking, quants, forced_qties)
        if picking.is_deposit:
            for rec in res:
                rec['owner_id'] = picking.owner_id.id
        return res


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    def _create_deposit_location(self):
        stock_location_obj = self.env['stock.location']
        stock_location_obj.create({
            'location_id': self.lot_stock_id.id,
            'name': 'Deposit Location',
            'deposit_location': True,
        })

    def _create_deposit_sequence(self, return_type=False):
        seq_obj = self.env['ir.sequence']
        dep_seq_id = seq_obj.create({
            'name': self.name + _(
                ' Sequence deposit %s') % ('in' if return_type else 'out'),
            'prefix':
                self.code + '/DEP/%s/' % ('IN' if return_type else 'OUT'),
            'padding': 5,
        })
        return dep_seq_id

    def _get_color(self):
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

    def _prepare_deposit_picking_type_values(self):
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
        }
        return res

    def _create_deposit_values(self):
        self._create_deposit_location()
        PickingType = self.env['stock.picking.type']
        vals = self._prepare_deposit_picking_type_values()
        PickingType.create(vals)
        vals_return = self._prepare_deposit_picking_type_return_values()
        PickingType.create(vals_return)

    @api.model
    def create(self, vals):
        warehouse = super(StockWarehouse, self).create(vals)
        warehouse._create_deposit_values()
        return warehouse


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _block_deposit_quants(self, domain):
        domain.append(('location_id.deposit_location', '=', False))
        return domain

    @api.model
    def quants_get(self, qty, move, ops=False, domain=None,
                   removal_strategy='fifo'):
        if move.location_dest_id.deposit_location:
            domain = self._block_deposit_quants(domain)
        elif not move.location_id.deposit_location and \
                not move.location_dest_id.deposit_location:
            domain = self._block_deposit_quants(domain)
        return super(StockQuant, self).quants_get(
            qty, move, ops, domain, removal_strategy)
