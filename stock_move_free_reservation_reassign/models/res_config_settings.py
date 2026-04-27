# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    reassign_stock_move_after_free_reservation = fields.Boolean(
        "Reassign moves unreserved by inventories",
        default=False,
        config_parameter="stock_move_free_reservation_reassign."
        "reassign_stock_move_after_free_reservation",
    )
