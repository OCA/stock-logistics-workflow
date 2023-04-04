# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.fields import first
from odoo.tools.rendering_tools import (
    parse_inline_template,
    render_inline_template,
    template_env_globals,
)


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    def _prepare_auto_lot_values(self):
        """
        Prepare multi valued lots per line to use multi creation.
        """
        self.ensure_one()
        vals = {"product_id": self.product_id.id, "company_id": self.company_id.id}
        if self.product_id.tracking == "lot":
            expression = self.picking_type_id.auto_create_lot_name_expression
            if expression:
                template_instructions = parse_inline_template(expression)
                variables = {"stock_move_line": self}
                variables.update(template_env_globals)
                vals["name"] = render_inline_template(template_instructions, variables)
        return vals

    def _get_and_create_lots(self):
        """
        Get existing lots and create missing ones.
        """
        vals_list = []
        stock_lot_obj = self.env["stock.lot"]
        lots = stock_lot_obj.browse()
        for line in self:
            vals = line._prepare_auto_lot_values()
            if line.picking_id.use_existing_lots and vals.get("name"):
                lot = stock_lot_obj.search(
                    [
                        (key, "=", vals[key])
                        for key in ("product_id", "company_id", "name")
                    ]
                )
                if lot:
                    lots |= lot
                else:
                    vals_list.append(vals)
            else:
                vals_list.append(vals)
        # Lots are created using create_multi to avoid too much queries.
        lots |= stock_lot_obj.create(vals_list)
        return lots

    def set_lot_auto(self):
        """
        Create lots and assign them. As move lines were created by product or
        by tracked 'serial' products, we apply the lot with both different
        approaches.
        """
        lots = self._get_and_create_lots()
        lots_by_product = dict()
        for lot in lots:
            if lot.product_id.id not in lots_by_product:
                lots_by_product[lot.product_id.id] = lot
            else:
                lots_by_product[lot.product_id.id] += lot
        for line in self:
            lot = first(lots_by_product[line.product_id.id])
            line.lot_id = lot
            if lot.product_id.tracking == "serial":
                lots_by_product[line.product_id.id] -= lot
