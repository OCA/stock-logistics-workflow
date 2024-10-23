# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class StockWarehouse(models.Model):

    _inherit = "stock.warehouse"

    use_loss_picking = fields.Boolean(
        string="Enable the Loss feature",
        help="Check this if you want to use the loss feature during picking operations.",
    )
    loss_location_id = fields.Many2one(
        comodel_name="stock.location",
    )
    loss_type_id = fields.Many2one(
        comodel_name="stock.picking.type", string="Loss Picking Type", help=""
    )
    loss_route_id = fields.Many2one(
        comodel_name="stock.route",
        help="This is a dummy field in order to create other values correctly",
    )

    def write(self, vals):
        warehouses = self.with_context(active_test=False)
        if "use_loss_picking" in vals:
            warehouses._update_location_loss(vals["use_loss_picking"])
        return super().write(vals)

    def _update_location_loss(self, use_loss_picking):
        self.mapped("loss_location_id").write({"active": use_loss_picking})

    # =========== Helper functions to initialize picking type, location ================

    def _get_locations_values(self, vals, code=False):
        values = super()._get_locations_values(vals, code=code)
        def_values = self.default_get(["company_id"])
        use_loss_picking = vals.get("use_loss_picking", False)
        code = vals.get("code") or code or ""
        code = code.replace(" ", "").upper()
        company_id = vals.get("company_id", def_values["company_id"])
        values.update(
            {
                "loss_location_id": {
                    "name": _("Loss Control"),
                    "active": use_loss_picking,
                    "usage": "internal",
                    "barcode": self._valid_barcode(code + "-LOSS", company_id),
                },
            }
        )
        return values

    def _get_picking_type_update_values(self):
        data = super()._get_picking_type_update_values()
        data.update(
            {
                "loss_type_id": {
                    "active": self.use_loss_picking and self.active,
                },
            }
        )
        return data

    def _get_picking_type_create_values(self, max_sequence):
        """When a warehouse is created this method return the values needed in
        order to create the new picking types for this warehouse. Every picking
        type are created at the same time than the warehouse howver they are
        activated or archived depending the delivery_steps or reception_steps.
        """
        data, next_sequence = super()._get_picking_type_create_values(max_sequence)
        data.update(
            {
                "loss_type_id": {
                    "name": _("Losses"),
                    "code": "internal",
                    "use_create_lots": False,
                    "use_existing_lots": True,
                    "default_location_src_id": self.lot_stock_id.id,
                    "default_location_dest_id": self.loss_location_id.id,
                    "sequence": next_sequence + 1,
                    "show_reserved": True,
                    "show_operations": True,
                    "sequence_code": "LOS",
                    "company_id": self.company_id.id,
                }
            }
        )
        return data, max_sequence + 20

    def get_rules_dict(self):
        """Define the rules source/destination locations, picking_type and
        action needed for each warehouse route configuration.
        """
        rules = super().get_rules_dict()
        for warehouse in self:
            rules[warehouse.id]["loss"] = []
        return rules

    def _get_routes_values(self):
        routes = super()._get_routes_values()
        routes.update(
            {
                "loss_route_id": {
                    "routing_key": "loss",
                    "depends": ["use_loss_picking"],
                    "route_create_values": {
                        "product_categ_selectable": False,
                        "warehouse_selectable": True,
                        "product_selectable": False,
                        "company_id": self.company_id.id,
                        "sequence": 10,
                        "name": self._format_routename(name=_("Loss Route (Dummy)")),
                    },
                    "route_update_values": {
                        "active": self.use_loss_picking,
                    },
                    "rules_values": {
                        "active": self.use_loss_picking,
                    },
                }
            }
        )
        return routes

    def _get_sequence_values(self, name=False, code=False):
        """Each picking type is created with a sequence. This method returns
        the sequence values associated to each picking type.
        """
        name = name if name else self.name
        code = code if code else self.code
        sequences = super()._get_sequence_values(name=name, code=code)
        sequences.update(
            {
                "loss_type_id": {
                    "name": name + " " + _("Loss Sequence"),
                    "prefix": code + "/LOSS/",
                    "padding": 5,
                    "company_id": self.company_id.id,
                },
            }
        )
        return sequences
