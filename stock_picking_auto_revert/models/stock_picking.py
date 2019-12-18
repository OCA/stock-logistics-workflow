# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, exceptions, _
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_revert_recreate(self):
        self.ensure_one()
        pick = self
        msg = _(
            "This picking cannot be returned because the products "
            "are not available in the destination location."
        )
        # Create return picking
        StockReturnPicking = self.env["stock.return.picking"]
        default_data = StockReturnPicking.with_context(
            active_ids=pick.ids, active_id=pick.id
        ).default_get(
            [
                "move_dest_exists",
                "original_location_id",
                "product_return_moves",
                "parent_location_id",
                "location_id",
            ]
        )
        for rm in default_data["product_return_moves"]:
            if len(rm) > 2 and isinstance(rm[2], dict):
                sm = pick.move_lines.filtered(
                    lambda x: x.product_id.id == rm[2]["product_id"]
                )
                precision = self.env["decimal.precision"].precision_get(
                    "Product Unit of Measure"
                )
                if (
                    float_compare(
                        rm[2]["quantity"],
                        sm.product_uom_qty,
                        precision_digits=precision,
                    )
                    < 0
                ):
                    raise exceptions.UserError(msg)
            else:
                raise exceptions.UserError(msg)
        return_wiz = StockReturnPicking.with_context(
            active_ids=pick.ids, active_id=pick.id
        ).create(default_data)
        try:
            res = return_wiz.create_returns()
        except exceptions.UserError:
            raise exceptions.UserError()

        return_pick = self.env["stock.picking"].browse(res["res_id"])

        # Validate picking
        operations = return_pick.mapped(
            "move_ids_without_package.move_line_ids"
        )
        for op in operations:
            op.qty_done = op.product_qty
        return_pick.button_validate()
        new_pick = pick.copy()

        # show the new picking
        action = self.env.ref("stock.action_picking_tree_all")
        result = action.read()[0]
        res = self.env.ref("stock.view_picking_form", False)
        result["views"] = [(res and res.id or False, "form")]
        result["res_id"] = new_pick.id
        return result
