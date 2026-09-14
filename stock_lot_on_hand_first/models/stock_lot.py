# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models
from odoo.osv.expression import AND


class StockLot(models.Model):
    _inherit = "stock.lot"

    @api.model
    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
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
                with_quantity_ids = self._search(
                    domain=with_quantity_domain,
                    offset=offset,
                    limit=limit,
                    order=order,
                )
                without_quantity_ids = self._search(
                    domain=AND([domain, [("product_qty", "=", 0)]]),
                    offset=0,
                    limit=limit - with_quantity_count,
                    order=order,
                )
                return self.browse(
                    self.browse(with_quantity_ids).ids
                    + self.browse(without_quantity_ids).ids
                )

        return super().search_fetch(
            domain=domain,
            field_names=field_names,
            offset=offset,
            limit=limit,
            order=order,
        )
