# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models
from odoo.osv.expression import AND


class StockLot(models.Model):
    _inherit = "stock.lot"

    @api.model
    def _name_search(self, name, domain=None, operator="ilike", limit=None, order=None):
        """Move lots without a qty on hand at the end of the list"""

        if self.env.context.get("name_search_qty_on_hand_first"):
            domain = list(domain or [])

            with_quantity_domain = AND([domain, [("product_qty", ">", 0)]])
            with_quantity_count = self.env["stock.lot"].search_count(
                with_quantity_domain
            )

            if with_quantity_count >= limit:
                domain = with_quantity_domain
            else:
                with_quantity_ids = super()._name_search(
                    name=name,
                    domain=with_quantity_domain,
                    operator=operator,
                    limit=limit,
                    order=order,
                )
                without_quantity_ids = super()._name_search(
                    name=name,
                    domain=AND([domain, [("product_qty", "=", 0)]]),
                    operator=operator,
                    limit=limit - with_quantity_count,
                    order=order,
                )
                # _name_search is supposed to return a odoo.osv.query.Query object that
                # will be evaluated as a list of ids when used in the browse function.
                # Since we cannot merge the Query objects to respect the intended order
                # in which we want to display the results,  we return the list of ids
                # that will be used by browse in the name_search implementation.
                return (
                    self.browse(with_quantity_ids).ids
                    + self.browse(without_quantity_ids).ids
                )

        return super()._name_search(
            name=name,
            domain=domain,
            operator=operator,
            limit=limit,
            order=order,
        )
