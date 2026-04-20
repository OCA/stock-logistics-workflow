# Copyright 2019 Camptocamp - Iryna Vyshnevska
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    use_oca_batch_validation = fields.Boolean()
    split_transfers_from_batch = fields.Boolean(default=False)
