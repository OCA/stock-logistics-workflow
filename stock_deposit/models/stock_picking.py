# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


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
            picking_type.is_deposit = (
                picking_type.default_location_dest_id.deposit_location or
                picking_type.default_location_src_id.deposit_location)

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
