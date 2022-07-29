# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    batch_picking_auto_invoice = fields.Selection(
        selection_add=[("sale_type", "By sale type")]
    )
