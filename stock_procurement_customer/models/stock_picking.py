# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    customer_id = fields.Many2one(
        comodel_name="res.partner",
        index=True,
    )
    customer_id_visible = fields.Boolean(
        compute="_compute_customer_id_visible",
        help="Technical field in order to say if the customer field should be visible.",
    )

    @api.depends("customer_id", "partner_id")
    def _compute_customer_id_visible(self):
        for picking in self:
            if picking.customer_id != picking.partner_id:
                picking.customer_id_visible = True
            else:
                picking.customer_id_visible = False
