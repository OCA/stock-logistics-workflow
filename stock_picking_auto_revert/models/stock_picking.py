# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, exceptions, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_revert_recreate(self):
        self.ensure_one()
        pick = self
        pick.move_ids._check_restrictions()
        # Create return picking
        StockReturnPicking = self.env["stock.return.picking"].with_context(
            active_model="stock.picking", active_id=pick.id
        )
        default_data = StockReturnPicking.default_get(
            [
                "move_dest_exists",
                "original_location_id",
                "product_return_moves",
                "parent_location_id",
                "location_id",
            ]
        )
        default_data.update({"location_id": pick.location_id.id})
        return_wiz = StockReturnPicking.create(default_data)
        return_wiz.picking_id = pick
        self._check_return_quantities(return_wiz, pick)
        res = return_wiz.create_returns()
        return_pick = self.env["stock.picking"].browse(res["res_id"])
        # Validate picking
        return_pick._action_done()
        new_pick = pick.copy()
        new_pick.origin = new_pick.origin + f" ({pick.name})"
        new_pick.action_assign()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        res = self.env.ref("stock.view_picking_form", False)
        result["views"] = [(res and res.id or False, "form")]
        result["res_id"] = new_pick.id
        return result

    def _check_return_quantities(self, return_wiz, pick):
        msg = _(
            "Too bad. This picking cannot be returned because the products "
            "are not available in the destination location"
        )
        for rm in return_wiz.product_return_moves:
            sm = pick.move_ids.filtered(
                lambda x, rm=rm: x.product_id.id == rm.product_id.id
                and x.state == "done"
            )
            if rm.quantity < sum(sm.mapped("product_uom_qty")):
                raise exceptions.UserError(msg)
