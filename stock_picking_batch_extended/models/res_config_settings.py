# Copyright 2019 Camptocamp - Iryna Vyshnevska
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_oca_batch_validation = fields.Boolean(
        string='Use OCA approach to validate Picking Batch',
        related="company_id.use_oca_batch_validation",
        readonly=False,
    )


class Company(models.Model):
    _inherit = "res.company"

    use_oca_batch_validation = fields.Boolean()
