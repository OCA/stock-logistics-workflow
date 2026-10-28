# Copyright 2025 Open Source Integrators (http://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.osv import expression


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _get_gather_domain(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
    ):
        domain = super()._get_gather_domain(
            product_id, location_id, lot_id, package_id, owner_id, strict
        )
        # Extend StockQuant to exclude locked lots from reservation domain
        # Block locked lots unless they have reserve_locked=False
        if not self.env.context.get("force_allow_locked_lots"):
            filter_domain = [
                "|",
                "|",
                ("lot_id", "=", False),
                ("lot_id.locked", "=", False),
                ("lot_id.locked_reservation", "=", False),
            ]
            domain = expression.AND([domain, filter_domain])
        return domain
