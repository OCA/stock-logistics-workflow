# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import models


class Product(models.Model):
    _inherit = "product.product"

    def _compute_quantities_dict(
        self, lot_id, owner_id, package_id, from_date=False, to_date=False
    ):
        owner_id = owner_id or False
        return super(
            Product, self.with_context(owner=owner_id)
        )._compute_quantities_dict(
            lot_id,
            owner_id,
            package_id,
            from_date=from_date,
            to_date=to_date,
        )
