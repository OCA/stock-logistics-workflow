# Copyright 2026 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_custom_move_fields(self):
        res = super()._get_custom_move_fields()
        res.append("restrict_partner_id")
        return res

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        values = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        values["restrict_partner_id"] = move_to_copy.restrict_partner_id.id
        return values
