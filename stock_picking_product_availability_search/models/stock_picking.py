# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv.expression import OR, distribute_not, normalize_domain


class StockPicking(models.Model):
    _inherit = "stock.picking"

    products_availability_state = fields.Selection(
        search="_search_products_availability_state"
    )

    @api.model
    def _search_products_availability_state(self, operator, value):
        if operator not in ("=", "!="):
            raise UserError(_("Invalid domain operator %s", operator))
        if not isinstance(value, str) and value is not False:
            raise UserError(_("Invalid domain right operand %s", value))
        # Search all pickings for which we need to compute the products availability.
        # The value would be ``False`` if the picking doesn't fall under this list.
        domain = [
            ("picking_type_code", "=", "outgoing"),
            ("state", "in", ["confirmed", "waiting", "assigned"]),
        ]
        # Special case for "is set" / "is not set" domains
        if operator == "=" and value is False:
            return distribute_not(["!"] + normalize_domain(domain))
        if operator == "!=" and value is False:
            return domain
        # Perform a search and compute values to filter on-the-fly
        res_ids = []
        pickings = self.with_context(prefetch_fields=False).search(domain)
        for picking in pickings:
            if picking.products_availability_state == value:
                res_ids.append(picking.id)
        if operator == "=":
            return [("id", "in", res_ids)]
        else:
            return OR(
                [
                    distribute_not(["!"] + normalize_domain(domain)),
                    [("id", "not in", res_ids)],
                ]
            )
