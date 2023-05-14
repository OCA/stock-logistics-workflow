# Copyright 2020 Carlos Dauden - Tecnativa
# Copyright 2020 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_quantities_dict(
        self, lot_id, owner_id, package_id, from_date=False, to_date=False
    ):
        if self.env.context.get("skip_restricted_owner"):
            return super()._compute_quantities_dict(
                lot_id, owner_id, package_id, from_date=from_date, to_date=to_date
            )
        restricted_owner_id = self.env.context.get("force_restricted_owner_id", None)
        if owner_id is None and restricted_owner_id is None:
            # Force owner to False if is None
            owner_id = False
        elif restricted_owner_id:
            owner_id = restricted_owner_id
        return super()._compute_quantities_dict(
            lot_id, owner_id, package_id, from_date=from_date, to_date=to_date
        )

    def _search_qty_available_new(
        self, operator, value, lot_id=False, owner_id=False, package_id=False
    ):
        new_self = self
        if not owner_id:
            new_self = self.with_context(force_restricted_owner_id=False)
        # Pass context variable to add domain in read group
        return super(ProductProduct, new_self)._search_qty_available_new(
            operator, value, lot_id=lot_id, owner_id=owner_id, package_id=package_id
        )
