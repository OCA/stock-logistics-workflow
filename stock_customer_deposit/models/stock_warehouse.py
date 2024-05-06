# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from collections import namedtuple

from odoo import _, api, fields, models

# namedtuple used in helper methods generating values for routes
Routing = namedtuple("Routing", ["from_loc", "dest_loc", "picking_type", "action"])


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    use_customer_deposits = fields.Boolean()
    customer_deposit_type_id = fields.Many2one(
        "stock.picking.type", "Customer Deposit Type", check_company=True
    )
    customer_deposit_route_id = fields.Many2one(
        "stock.route", "Customer Deposit Route", ondelete="restrict"
    )

    @api.model_create_multi
    def create(self, vals_list):
        warehouses = super().create(vals_list)
        for warehouse in warehouses:
            if warehouse.use_customer_deposits:
                # create sequences and operation type for customer deposit
                new_vals = (
                    warehouse._create_or_update_deposit_sequences_and_picking_types()
                )
                warehouse.write(new_vals)
                # create routes and rules for customer deposit
                warehouse._create_or_update_customer_deposit_route()
        return warehouses

    def write(self, vals):
        warehouses = self.with_context(active_test=False)

        if vals.get("code") or vals.get("name"):
            warehouses._update_customer_deposit_name_and_code(
                vals.get("name"), vals.get("code")
            )

        res = super().write(vals)

        for warehouse in warehouses:
            if "use_customer_deposits" in vals:
                if warehouse.use_customer_deposits:
                    picking_type_vals = (
                        warehouse._create_or_update_deposit_sequences_and_picking_types()
                    )
                    if picking_type_vals:
                        warehouse.write(picking_type_vals)
                    warehouse._create_or_update_customer_deposit_route()
                else:
                    warehouse._deactivate_customer_deposit()
        return res

    def _create_or_update_deposit_sequences_and_picking_types(self):
        self.ensure_one()
        IrSequenceSudo = self.env["ir.sequence"].sudo()
        PickingType = self.env["stock.picking.type"]

        warehouse_data = {}
        sequence_data = self._get_customer_deposit_sequence_values()

        data = self._get_customer_deposit_picking_type_update_values()

        if self.customer_deposit_type_id:
            self.customer_deposit_type_id.sudo().sequence_id.write(sequence_data)
            self.customer_deposit_type_id.write(data)
        else:
            max_sequence = self.env["stock.picking.type"].search_read(
                [("sequence", "!=", False)],
                ["sequence"],
                limit=1,
                order="sequence desc",
            )
            max_sequence = max_sequence and max_sequence[0]["sequence"] or 0
            (
                create_data,
                max_sequence,
            ) = self._get_customer_deposit_picking_type_create_values(max_sequence)
            data.update(create_data)
            existing_sequence = IrSequenceSudo.search_count(
                [
                    ("company_id", "=", sequence_data["company_id"]),
                    ("name", "=", sequence_data["name"]),
                ],
                limit=1,
            )
            sequence = IrSequenceSudo.create(sequence_data)
            if existing_sequence:
                sequence.name = _(
                    "%(name)s (copy)(%(id)s)", name=sequence.name, id=str(sequence.id)
                )
            data.update(warehouse_id=self.id, sequence_id=sequence.id)
            warehouse_data["customer_deposit_type_id"] = PickingType.create(data).id

        return warehouse_data

    def _create_or_update_customer_deposit_route(self):
        # Create customer deposit route and active/create their related rules.
        rules_dict = self.get_customer_deposit_rules_dict()
        route_data = self._get_customer_deposit_route_values()
        # If the route exists update it
        if self.customer_deposit_route_id:
            route = self.customer_deposit_route_id
            if "route_update_values" in route_data:
                route.write(route_data["route_update_values"])
            route.rule_ids.write({"active": False})
        # Create the route
        else:
            if "route_update_values" in route_data:
                route_data["route_create_values"].update(
                    route_data["route_update_values"]
                )
            route = self.env["stock.route"].create(route_data["route_create_values"])
            self.customer_deposit_route_id = route

        # Get rules needed for the route
        routing_key = route_data.get("routing_key")
        rules = rules_dict[self.id][routing_key]
        if "rules_values" in route_data:
            route_data["rules_values"].update({"route_id": route.id})
        else:
            route_data["rules_values"] = {"route_id": route.id}
        rules_list = self._get_rule_values(rules, values=route_data["rules_values"])
        # Create/Active rules
        self._find_existing_rule_or_create(rules_list)

    def _get_customer_deposit_route_values(self):
        return {
            "routing_key": "customer_deposits",
            "depends": ["delivery_steps", "reception_steps"],
            "route_update_values": {
                "name": self._format_routename(name=_("Customer Deposit")),
                "active": self.active,
            },
            "route_create_values": {
                "product_categ_selectable": False,
                "warehouse_selectable": False,
                "product_selectable": False,
                "sale_selectable": True,
                "company_id": self.company_id.id,
                "sequence": 9,
            },
            "rules_values": {
                "active": True,
                "propagate_cancel": True,
            },
        }

    def get_customer_deposit_rules_dict(self):
        customer_loc, supplier_loc = self._get_partner_locations()
        return {
            warehouse.id: {
                "customer_deposits": [
                    self.Routing(
                        warehouse.lot_stock_id,
                        customer_loc,
                        warehouse.customer_deposit_type_id,
                        "pull",
                    ),
                ]
            }
            for warehouse in self
        }

    def _update_customer_deposit_name_and_code(self, new_name=False, new_code=False):
        for warehouse in self:
            if self.use_customer_deposits:
                sequence_data = warehouse._get_customer_deposit_sequence_values(
                    name=new_name, code=new_code
                )
                if self.user_has_groups("stock.group_stock_manager"):
                    warehouse = warehouse.sudo()
                warehouse.customer_deposit_type_id.sequence_id.write(sequence_data)

    def _get_customer_deposit_picking_type_update_values(self):
        customer_loc, supplier_loc = self._get_partner_locations()
        return {
            "active": self.use_customer_deposits,
            "assign_owner": False,
            "code": "internal",
            "default_location_src_id": self.lot_stock_id.id,
            "default_location_dest_id": customer_loc.id,
            "barcode": self.code.replace(" ", "").upper() + "-DEPOSIT",
        }

    def _get_customer_deposit_picking_type_create_values(self, max_sequence):
        customer_loc, supplier_loc = self._get_partner_locations()
        return {
            "code": "internal",
            "name": _("Customer Deposit"),
            "use_create_lots": False,
            "use_existing_lots": True,
            "assign_owner": True,
            "default_location_src_id": self.lot_stock_id.id,
            "default_location_dest_id": self.lot_stock_id.id,
            "sequence": max_sequence + 1,
            "show_reserved": False,
            "show_operations": True,
            "sequence_code": "DEPOSIT",
            "company_id": self.company_id.id,
        }, max_sequence + 1

    def _get_customer_deposit_sequence_values(self, name=False, code=False):
        name = name if name else self.name
        code = code if code else self.code
        return {
            "name": _("%s Sequence Customer Deposit", name),
            "prefix": code + "/DEPOSIT/",
            "padding": 5,
            "company_id": self.company_id.id,
        }

    def _deactivate_customer_deposit(self):
        for warehouse in self:
            warehouse.customer_deposit_type_id.write({"active": False})
            warehouse.customer_deposit_route_id.write({"active": False})

    def _get_all_routes(self):
        routes = super()._get_all_routes()
        routes |= self.mapped("customer_deposit_route_id")
        return routes
