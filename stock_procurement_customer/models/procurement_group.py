# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProcurementGroup(models.Model):

    _inherit = "procurement.group"

    customer_id = fields.Many2one(
        comodel_name="res.partner",
    )
