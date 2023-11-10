# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    inter_warehouse_transfers = fields.Boolean("Inter-Warehouse Transfers")

    receipt_destination_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Receipt Destination Location",
        help="Destination location where products will be received",
    )
    receipt_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Receipt Operation Type",
        help="Operation type for incoming inter-warehouse pickings",
    )
    receipt_picking_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner in Picking",
        help="Receiving picking partner",
    )

    def write(self, vals):
        res = super().write(vals)
        for wh in self:
            route_inter_warehouse = self.env.ref(
                "stock_picking_inter_warehouse.stock_location_route_inter_warehouse"
            )
            if wh.inter_warehouse_transfers:
                # Add the warehouse to the route
                # for inter-warehouse transfers
                route_inter_warehouse.write(
                    {
                        "warehouse_ids": [(4, wh.id)],
                    }
                )

                # Create the location needed for the transfers
                company_internal_transit_location = (
                    wh.company_id.internal_transit_location_id
                )
                if not company_internal_transit_location.active:
                    company_internal_transit_location.write(
                        {
                            "active": True,
                        }
                    )

                location_src_id = (
                    wh.receipt_picking_partner_id.default_stock_location_src_id
                )
                if not location_src_id:
                    location_src_id = self.env["stock.location"].create(
                        {
                            "name": wh.name,
                            "location_id": company_internal_transit_location.id,
                            "inter_warehouse_partner_id": [
                                (6, 0, wh.receipt_picking_partner_id.ids)
                            ],
                        }
                    )

                # Create or edit the rule used for
                # managing inter-warehouse transfers
                rule_vals = {
                    "name": self._format_rulename(
                        location_src_id,
                        wh.receipt_destination_location_id,
                        _("Inter-Warehouse"),
                    ),
                    "action": "push",
                    "picking_type_id": wh.receipt_picking_type_id.id,
                    "location_src_id": location_src_id.id,
                    "location_id": wh.receipt_destination_location_id.id,
                    "route_id": route_inter_warehouse.id,
                    "auto": "manual",
                    "company_id": wh.company_id.id,
                    "inter_warehouse_src_id": wh.id,
                }

                rule_id = route_inter_warehouse.rule_ids.filtered(
                    lambda x: x.inter_warehouse_src_id == wh
                )
                if rule_id:
                    rule_id.write(rule_vals)
                else:
                    self.env["stock.rule"].create(rule_vals)
            elif not vals.get("inter_warehouse_transfers", True):
                # inter_warehouse_transfers has been disabled
                # we have to archive the rule that has been made
                rule_id = route_inter_warehouse.rule_ids.filtered(
                    lambda x: x.inter_warehouse_src_id == wh
                )
                route_inter_warehouse.write(
                    {
                        "warehouse_ids": [(3, wh.id)],
                        "rule_ids": [(2, rule_id.id)],
                    }
                )
        return res
