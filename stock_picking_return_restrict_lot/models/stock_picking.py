# Copyright 2023 Foodles (https://www.foodles.com/)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def action_stock_picking_full_return(self):
        return_pickings = self._action_stock_pickings_full_return()

        # TODO: improve to manage multiple returns at once
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_partner_id": return_pickings.partner_id.id,
                "search_default_picking_type_id": return_pickings.picking_type_id.id,
                "search_default_draft": False,
                "search_default_assigned": False,
                "search_default_confirmed": False,
                "search_default_ready": False,
                "search_default_planning_issues": False,
                "search_default_available": False,
            }
        )

        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )

        if len(return_pickings) == 1:
            action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action["res_id"] = return_pickings.id
        else:
            action["domain"] = [("id", "in", return_pickings.ids)]
        action["name"] = _("Returned Picking")
        action["context"] = ctx
        return action

    def _action_stock_pickings_full_return(self):
        return_pickings = self.env["stock.picking"].browse()
        for picking in self:
            return_pickings |= picking._create_full_return()
        return return_pickings

    # inspired from odoo.addons.stock.wizard.stock_picking_return

    def _create_full_return(self):
        self.ensure_one()
        for return_move in self.move_lines:
            return_move.move_dest_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            )._do_unreserve()

        # create new picking for returned products
        picking_type_id = (
            self.picking_type_id.return_picking_type_id.id or self.picking_type_id.id
        )
        new_picking = self.copy(
            {
                "move_lines": [],
                "picking_type_id": picking_type_id,
                "state": "draft",
                "origin": _("Return of %s", self.name),
                "location_id": self.location_dest_id.id,
                "location_dest_id": self.location_id.id,
            }
        )
        new_picking.message_post_with_view(
            "mail.message_origin_link",
            values={"self": new_picking, "origin": self},
            subtype_id=self.env.ref("mail.mt_note").id,
        )

        for return_line in self.move_line_ids:
            if return_line.qty_done and return_line.state == "done":
                vals = self._prepare_return_move_default_values(
                    return_line, new_picking
                )
                r = return_line.move_id.copy(vals)
                vals = {}

                move_orig_to_link = return_line.move_id.move_dest_ids.mapped(
                    "returned_move_ids"
                )
                # link to original move
                move_orig_to_link |= return_line.move_id
                # link to siblings of original move, if any
                move_orig_to_link |= (
                    return_line.move_id.mapped("move_dest_ids")
                    .filtered(lambda m: m.state not in ("cancel"))
                    .mapped("move_orig_ids")
                    .filtered(lambda m: m.state not in ("cancel"))
                )
                move_dest_to_link = return_line.move_id.move_orig_ids.mapped(
                    "returned_move_ids"
                )
                move_dest_to_link |= (
                    return_line.move_id.move_orig_ids.mapped("returned_move_ids")
                    .mapped("move_orig_ids")
                    .filtered(lambda m: m.state not in ("cancel"))
                    .mapped("move_dest_ids")
                    .filtered(lambda m: m.state not in ("cancel"))
                )
                vals["move_orig_ids"] = [(4, m.id) for m in move_orig_to_link]
                vals["move_dest_ids"] = [(4, m.id) for m in move_dest_to_link]
                r.write(vals)

        new_picking.action_confirm()
        new_picking.action_assign()
        return new_picking

    def _prepare_return_move_default_values(self, stock_move_line, new_picking):
        vals = {
            "product_id": stock_move_line.product_id.id,
            "product_uom_qty": stock_move_line.qty_done,
            "product_uom": stock_move_line.product_id.uom_id.id,
            "picking_id": new_picking.id,
            "state": "draft",
            "date": fields.Datetime.now(),
            "location_id": stock_move_line.location_dest_id.id,
            "location_dest_id": stock_move_line.location_id.id,
            "picking_type_id": new_picking.picking_type_id.id,
            "warehouse_id": stock_move_line.picking_id.picking_type_id.warehouse_id.id,
            "origin_returned_move_id": stock_move_line.move_id.id,
            "restrict_lot_id": stock_move_line.lot_id.id,
            "procure_method": "make_to_stock",
        }
        return vals
