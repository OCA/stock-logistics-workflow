# Copyright 2026 arielbarreiros96 (https://github.com/arielbarreiros96)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _portal_is_returnable(self):
        """Whether the customer may get the return slip of this operation."""
        self.ensure_one()
        return (
            self.state == "done"
            and self.picking_type_code == "outgoing"
            and not self.return_id
        )
