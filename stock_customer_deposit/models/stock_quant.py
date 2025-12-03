# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import api, models
from odoo.osv import expression
from odoo.tools import float_compare


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
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
        if owner_id:
            return domain
        if self.env.context.get("owner"):
            domain = expression.AND(
                [domain, [("owner_id", "parent_of", self.env.context["owner"])]]
            )
        else:
            domain = expression.AND([domain, [("owner_id", "=", False)]])
        return domain

    @api.model
    def _update_available_quantity(
        self,
        product_id,
        location_id,
        quantity=False,
        reserved_quantity=False,
        lot_id=None,
        package_id=None,
        owner_id=None,
        in_date=None,
    ):
        if (
            float_compare(quantity, 0.0, precision_rounding=product_id.uom_id.rounding)
            > 0
            and self.env.context.get("owner")
            and not owner_id
        ):
            owner_id = self.env["res.partner"].browse(self.env.context["owner"])
        return super()._update_available_quantity(
            product_id,
            location_id,
            quantity,
            reserved_quantity,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            in_date=in_date,
        )
