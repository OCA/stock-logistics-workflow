# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import UserError, ValidationError


class Picking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "tier.validation"]
    _state_from = ["draft", "waiting", "confirmed", "assigned"]
    _state_to = ["done"]
