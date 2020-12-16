# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    batch_picking_auto_invoice = fields.Boolean(
        company_dependent=True,
    )

    @api.model
    def _commercial_fields(self):
        res = super()._commercial_fields()
        return res + ['batch_picking_auto_invoice']
