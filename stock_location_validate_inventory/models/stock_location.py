# Copyright 2026 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = "stock.location"

    def validate_inventory(self):
        """Validate the current stock of the location.

        This reset any counted difference quantity on the quants and update the
        location last inventory date.
        """
        if not (
            self.env.user.has_group(
                "stock_location_validate_inventory.group_stock_location_can_validate_inventory"
            )
        ):
            raise UserError(_("You are not allowed to validate the location inventory"))
        self.quant_ids.action_set_inventory_quantity_to_zero()
        self.sudo().last_inventory_date = fields.Date.today()
