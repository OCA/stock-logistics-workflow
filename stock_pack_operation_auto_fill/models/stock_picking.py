# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
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

    @api.multi
    def _check_action_pack_operation_auto_fill_allowed(self):
        if any(not r.action_pack_op_auto_fill_allowed for r in self):
            raise UserError(
                _("Filling the operations automatically is not possible, "
                  "perhaps the pickings aren't in the right state "
                  "(Partially available or available)."))

    @api.multi
    def action_pack_operation_auto_fill(self):
        """ Fill automatically pack operation for products with the following
        conditions:
            - there is no tracking set on the product (i.e tracking is none).
            this condition can be checked by the field `lots_visible` on the
            pack operation model.
            - the package is not required, the package is required if the
            the no product is set on the operation.
            - the operation has no qty_done yet.
        """
        self._check_action_pack_operation_auto_fill_allowed()
        operations = self.mapped('pack_operation_ids')
        operations_to_auto_fill = operations.filtered(
            lambda op: not op.lots_visible and op.product_id and
            not op.qty_done)
        for op in operations_to_auto_fill:
            op.qty_done = op.product_qty
