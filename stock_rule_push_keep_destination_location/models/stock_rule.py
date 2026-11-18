# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    use_rule_destination_location = fields.Boolean(
        help="Check this in order to use this push rule destination location instead of"
        " the original move final location destination."
    )

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        """
        If the destination location of the preceding move is pointing to a
        child of the push rule destination location, Odoo keeps the original
        destination location instead of using the push rule one.

        This is annoying if putaway rules are defined on that wanted destination
        location.

        We will use a configuration parameter on push rule to force the rule
        destination location instead.
        """
        result = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        if self.use_rule_destination_location:
            result["location_dest_id"] = self.location_dest_id.id
        return result
