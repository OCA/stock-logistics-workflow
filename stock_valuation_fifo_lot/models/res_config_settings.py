# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_lot_get_price_unit_fifo = fields.Boolean(
        related="company_id.use_lot_get_price_unit_fifo",
        readonly=False,
        help="Use the FIFO price unit by lot when there is no PO.",
    )
