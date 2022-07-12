# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    is_moves_assignation_limited = fields.Boolean()
    moves_assignation_horizon = fields.Integer()
