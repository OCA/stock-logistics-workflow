# Copyright 2026 Ecosoft (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    fiscal_position_id = fields.Many2one(
        comodel_name="account.fiscal.position",
        check_company=True,
        ondelete="restrict",
        help="Fiscal positions are used to adapt taxes and accounts for particular "
        "customers or sales orders/invoices. "
        "The default value comes from the customer.",
    )
