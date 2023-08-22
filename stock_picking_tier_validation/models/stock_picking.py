# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "tier.validation"]
    _state_from = ["draft", "waiting", "confirmed", "assigned"]
    _state_to = ["done", "approved"]

    _tier_validation_manual_config = False
