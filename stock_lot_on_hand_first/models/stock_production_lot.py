# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models
from odoo.osv.expression import AND


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.model
    def _name_search(self, name="", args=None, operator="ilike", limit=80):
        """Move lots without a qty on hand at the end of the list"""

        if self.env.context.get("name_search_qty_on_hand_first"):
            args = list(args or [])

            with_quantity_domain = AND([args, [("product_qty", ">", 0)]])
            with_quantity_count = self.env["stock.production.lot"].search_count(
                with_quantity_domain
            )

            if with_quantity_count >= limit:
                args = with_quantity_domain
            else:
                with_quantity_ids = super()._name_search(
                    name=name, args=with_quantity_domain, operator=operator, limit=limit
                )
                without_quantity_ids = super()._name_search(
                    name=name,
                    args=AND([args, [("product_qty", "=", 0)]]),
                    operator=operator,
                    limit=limit - with_quantity_count,
                )
                # _name_search is supposed to return a odoo.osv.query.Query object
                # that will be evaluated as a list of ids when used in the browse function.
                # Since we cannot merge the Query objects to respect the intended order
                # in which we want to display the results,  we return the list of ids
                # that will be used by browse in the name_search implementation.
                return (
                    self.browse(with_quantity_ids).ids
                    + self.browse(without_quantity_ids).ids
                )

        return super()._name_search(
            name=name, args=args, operator=operator, limit=limit
        )
