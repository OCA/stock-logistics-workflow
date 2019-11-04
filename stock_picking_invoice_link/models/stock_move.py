# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2015-2016 AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    invoice_line_ids = fields.Many2many(
        comodel_name='account.invoice.line',
        relation='stock_move_invoice_line_rel',
        column1='move_id',
        column2='invoice_line_id',
        string='Invoice Line',
        copy=False,
        readonly=True,
    )

    def write(self, vals):
        """
        User can update any picking in done state, but if this picking already
        invoiced the stock move done quantities can be different to invoice
        line quantities. So to avoid this inconsistency you can not update any
        stock move line in done state and have invoice lines linked.
        """
        if 'product_uom_qty' in vals:
            for move in self:
                if move.state == 'done' and move.invoice_line_ids:
                    raise UserError(
                        _('You can not modify an invoiced stock move'))
        return super().write(vals)
