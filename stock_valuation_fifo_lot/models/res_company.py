# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    use_lot_get_price_unit_fifo = fields.Boolean(
        default=True, help="Use the FIFO price unit by lot when there is no PO."
    )
