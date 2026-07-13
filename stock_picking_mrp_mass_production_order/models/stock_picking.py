# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Picking(models.Model):
    _inherit = "stock.picking"

    mrp_picking_ids = fields.One2many(
        "mrp.production",
        "manufacturing_picking_id",
        string="Manufacturing Picking Orders",
    )
    mrp_picking_count = fields.Integer(
        compute="_compute_mrp_picking_count",
    )

    @api.depends("mrp_picking_count")
    def _compute_mrp_picking_count(self):
        for cpr in self:
            cpr.mrp_picking_count = len(cpr.mrp_picking_ids)

    def action_mrp_mass_production_order(self):
        self.ensure_one()
        if self.state == "done" and self.picking_type_code in [
            "incoming",
            "internal",
            "stock_request_order",
        ]:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "mrp_mass_production_order.wizard_mass_mrp_production_order_action"
            )
            entries = []
            products = []
            for move_id in self.move_ids.filtered(
                lambda x: x.consumed_quantity < x.product_uom_qty
            ):
                if move_id.product_id.id in products:
                    continue
                products.append(move_id.product_id.id)
                entries.append(
                    self.env["mrp.mass.production.order.entry.wizard"]
                    .create(
                        {
                            "product_id": move_id.product_id.id,
                            "product_consumed_id": move_id.product_id.id,
                        }
                    )
                    .id
                )
            if entries:
                action.update(
                    {
                        "view_mode": "form",
                        "views": [(False, "form")],
                        "name": _("Create Mass Production Orders"),
                        "context": {
                            "default_mrp_production_order_entries": entries,
                            "default_with_bom": False,
                        },
                    }
                )
                return action
            else:
                raise ValidationError(_("There are no products to consume"))
        else:
            raise ValidationError(
                _(
                    "Operation not allowed: this action can only be performed when the "
                    "transfer is validated and the picking type is "
                    "either 'Incoming' or 'Internal' or 'Stock Request Order'."
                )
            )

    def action_view_mrp_picking_ids(self):
        return {
            "name": "Manufacturing Orders - " + self.name,
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "mrp.production",
            "domain": [("id", "in", self.mrp_picking_ids.ids)],
        }
