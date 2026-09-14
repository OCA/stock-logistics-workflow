# Copyright 2026 Ecosoft (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    fiscal_position_id = fields.Many2one(
        comodel_name="account.fiscal.position",
        compute="_compute_fiscal_position_id",
        store=True,
        check_company=True,
        ondelete="restrict",
        help="Fiscal positions are used to adapt taxes and accounts for particular "
        "customers or sales orders/invoices. "
        "The value is set only when configured on the operation type.",
    )

    @api.depends("picking_type_id")
    def _compute_fiscal_position_id(self):
        for rec in self:
            rec.fiscal_position_id = rec.picking_type_id.fiscal_position_id or False
