# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.stock.models.stock_rule import ProcurementGroup


class ZoneLocationSourceCommon:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.PickingType = cls.env["stock.picking.type"]
        cls.Location = cls.env["stock.location"]
        cls.Product = cls.env["product.product"]
        cls.Route = cls.env["stock.route"]
        cls.Rule = cls.env["stock.rule"]
        cls.Quant = cls.env["stock.quant"]
        cls.Picking = cls.env["stock.picking"]
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.warehouse = cls.env.ref("stock.warehouse0")

        # Create a Stock structure as is:

        #                                  WH (view)
        #
        #   FOOD(view/zone/source)     STOCK (zone/source)   PHARMA(view/zone/source)
        #
        #            FOOD 1                                           PHARMA 1

        # Set delivery in three steps in order to check
        # the good origin
        cls.warehouse.delivery_steps = "pick_pack_ship"

        # Create several picking zones (e.g.: Pharmaceutical, Food)
        cls.pharma_location = cls.Location.create(
            {
                "name": "Pharmaceutical",
                "location_id": cls.warehouse.lot_stock_id.id,
                "usage": "view",
                "is_considered_as_source": True,
                "is_zone": True,
            }
        )

        cls.pharma_location_1 = cls.Location.create(
            {
                "name": "Pharmaceutical 1",
                "location_id": cls.pharma_location.id,
            }
        )

        cls.pharma_type = cls.PickingType.create(
            {
                "name": "Picking Pharmaceutical",
                "sequence_code": "PHARMA",
                "code": "internal",
                "default_location_src_id": cls.pharma_location.id,
                "default_location_dest_id": cls.warehouse.wh_pack_stock_loc_id.id,
            }
        )

        cls.food_location = cls.Location.create(
            {
                "name": "Food",
                "location_id": cls.warehouse.lot_stock_id.id,
                "usage": "view",
                "is_considered_as_source": True,
                "is_zone": True,
            }
        )
        cls.food_location_1 = cls.Location.create(
            {
                "name": "Food 1",
                "location_id": cls.food_location.id,
            }
        )
        # Set stock as source too
        cls.warehouse.lot_stock_id.is_zone = True
        cls.warehouse.lot_stock_id.is_considered_as_source = True
        cls.food_type = cls.PickingType.create(
            {
                "name": "Picking Food",
                "sequence_code": "FOOD",
                "code": "internal",
                "default_location_src_id": cls.food_location.id,
                "default_location_dest_id": cls.warehouse.wh_pack_stock_loc_id.id,
            }
        )

        # Create products
        cls.pharma_product = cls.Product.create(
            {
                "name": "Pharma Product",
                "type": "product",
            }
        )
        cls.food_product = cls.Product.create(
            {
                "name": "Food Product",
                "type": "product",
            }
        )
        # This one will use Stock
        cls.normal_product = cls.Product.create(
            {
                "name": "Normal Product",
                "type": "product",
            }
        )

        cls.products = cls.pharma_product + cls.food_product + cls.normal_product

        # Create Routes
        cls.pharma_route = cls.Route.create(
            {
                "name": "The Pharma route",
                "sequence": 50,
            }
        )
        cls.food_route = cls.Route.create(
            {
                "name": "The Food route",
                "sequence": 50,
            }
        )

        cls.Rule.create(
            {
                "name": "Pharma > Pack",
                "location_dest_id": cls.warehouse.wh_pack_stock_loc_id.id,
                "procure_method": "make_to_stock",
                "location_src_id": cls.pharma_location.id,
                "action": "pull",
                "route_id": cls.pharma_route.id,
                "picking_type_id": cls.pharma_type.id,
            }
        )

        cls.Rule.create(
            {
                "name": "Food > Pack",
                "location_dest_id": cls.warehouse.wh_pack_stock_loc_id.id,
                "procure_method": "make_to_stock",
                "location_src_id": cls.food_location.id,
                "action": "pull",
                "route_id": cls.food_route.id,
                "picking_type_id": cls.food_type.id,
            }
        )

        # Assign routes
        cls.pharma_product.route_ids |= cls.pharma_route
        cls.food_product.route_ids |= cls.food_route

        # Create quantities
        cls._create_inventory(cls.pharma_product, 10.0, cls.pharma_location_1)
        cls._create_inventory(cls.food_product, 15.0, cls.food_location_1)
        cls._create_inventory(cls.normal_product, 20.0, cls.warehouse.lot_stock_id)

    @classmethod
    def _create_inventory(cls, product, qty, location):
        cls.Quant.with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "inventory_quantity": qty,
                "location_id": location.id,
            }
        )._apply_inventory()

    @classmethod
    def _create_customer_need(cls):
        procurements = list()
        procurements.append(
            ProcurementGroup.Procurement(
                cls.pharma_product,
                5.0,
                cls.pharma_product.uom_id,
                cls.customers,
                "Pharma",
                "Customer",
                cls.env.company,
                {"warehouse_id": cls.warehouse},
            )
        )
        procurements.append(
            ProcurementGroup.Procurement(
                cls.food_product,
                4.0,
                cls.food_product.uom_id,
                cls.customers,
                "Food",
                "Customer",
                cls.env.company,
                {"warehouse_id": cls.warehouse},
            )
        )

        procurements.append(
            ProcurementGroup.Procurement(
                cls.normal_product,
                6.0,
                cls.normal_product.uom_id,
                cls.customers,
                "Normal",
                "Customer",
                cls.env.company,
                {"warehouse_id": cls.warehouse},
            )
        )

        cls.env["procurement.group"].run(procurements)
