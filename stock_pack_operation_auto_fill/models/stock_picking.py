# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    action_pack_op_auto_fill_allowed = fields.Boolean(
        compute='_compute_action_pack_operation_auto_fill_allowed',
        readonly=True,
    )

    @api.depends('state', 'pack_operation_ids')
    def _compute_action_pack_operation_auto_fill_allowed(self):
        """ The auto fill button is allowed only in availabe or partially
        available state, and the picking have pack operations.
        """
        for rec in self:
            rec.action_pack_op_auto_fill_allowed = \
                rec.state in ['partially_available', 'assigned'] and \
                rec.pack_operation_ids

    def _check_action_pack_operation_auto_fill_allowed(self):
        if any(not r.action_pack_op_auto_fill_allowed for r in self):
            raise UserError(
                _("Filling the operations automatically is not possible, "
                  "perhaps the pickings aren't in the right state "
                  "(Partially available or available)."))

    def action_pack_operation_auto_fill(self):
        """ Fill automatically pack operation for products with the following
        conditions:
            - the package is not required, the package is required if the
            the no product is set on the operation.
            - the operation has no qty_done yet.
        """
        self.ensure_one()
        self._check_action_pack_operation_auto_fill_allowed()
        prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for op in self.pack_operation_ids:
            if not float_is_zero(op.qty_done, precision_digits=prec):
                continue
            new_qty_done = 0
            if op.product_id.tracking in ('lot', 'serial'):
                if op.pack_lot_ids:
                    for opl in op.pack_lot_ids:
                        if float_compare(
                                opl.qty, opl.qty_todo, precision_digits=prec):
                            opl.qty = opl.qty_todo
                        new_qty_done += opl.qty
            else:
                new_qty_done = op.product_qty
            if (
                    new_qty_done and
                    float_compare(
                    op.qty_done, new_qty_done, precision_digits=prec)):
                op.qty_done = new_qty_done
