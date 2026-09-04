# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase


class OperationLossQuantityCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.quant_obj = cls.env["stock.quant"]

        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "Tracking Lot",
                "tracking": "lot",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "No Tracking",
                "tracking": "none",
            }
        )
        cls.product_3 = cls.env["product.product"].create(
            {
                "name": "Product 3",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "No Tracking",
                "tracking": "none",
            }
        )
        wh = cls.env["stock.warehouse"].search([], limit=1)
        cls.loc_stock = wh.lot_stock_id

        cls.loc_customer = cls.env.ref("stock.stock_location_customers")

        cls.pick_type_out = cls.env.ref("stock.picking_type_out")
        cls.warehouse = wh
        cls.warehouse.use_loss_picking = True

        # Set user in notification group
        group = cls.env.ref(
            "stock_picking_operation_loss_quantity.group_loss_notification"
        )
        cls.user_demo = cls.env.ref("base.user_demo")
        group.users += cls.user_demo

    @classmethod
    def initiate_values(cls):
        cls.product_1_lotA = cls.env["stock.lot"].create(
            {"product_id": cls.product_1.id, "name": "LotA"}
        )
        cls.product_1_lotB = cls.env["stock.lot"].create(
            {"product_id": cls.product_1.id, "name": "LotB"}
        )

        # Create picking 1
        cls.picking_1 = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.pick_type_out.id,
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
            }
        )
        cls.move_1 = cls.env["stock.move"].create(
            {
                "picking_id": cls.picking_1.id,
                "name": "Test move",
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_uom_qty": 7,
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
                "date": "2018-01-01 00:00:00",
            }
        )
        cls.move_1._action_confirm()

        # Put product in stock
        # LotA: 3
        # LotB: 5
        cls._create_quantities(cls.product_1, 3.0, lot=cls.product_1_lotA)
        cls._create_quantities(cls.product_1, 5.0, lot=cls.product_1_lotB)

        cls.picking_1.action_assign()

    @classmethod
    def initiate_values_no_tracking(cls):
        # Create picking 2
        cls.picking_2 = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.pick_type_out.id,
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
            }
        )
        cls.move_2 = cls.env["stock.move"].create(
            {
                "picking_id": cls.picking_2.id,
                "name": "Test move 2",
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "product_uom_qty": 6,
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
                "date": "2018-01-01 00:00:00",
            }
        )
        cls.move_2._action_confirm()
        cls.move_3 = cls.env["stock.move"].create(
            {
                "picking_id": cls.picking_2.id,
                "name": "Test move 3",
                "product_id": cls.product_3.id,
                "product_uom": cls.product_3.uom_id.id,
                "product_uom_qty": 2,
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
                "date": "2018-01-01 00:00:00",
            }
        )
        cls.move_3._action_confirm()

        # Put product in stock
        cls._create_quantities(cls.product_2, 10.0)
        cls._create_quantities(cls.product_3, 10.0)

        cls.picking_2.action_assign()

    @classmethod
    def _create_quantities(
        cls, product, quantity, location=None, lot=None, package=None
    ):
        cls.quant_obj.with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "inventory_quantity": quantity,
                "location_id": location.id if location else cls.loc_stock.id,
                "lot_id": lot.id if lot else False,
                "package_id": package.id if package else False,
            }
        )._apply_inventory()

    def setUp(self):
        super().setUp()
        self.loss_pickings_before = self.env["stock.picking"].search(
            self._loss_pickings_domain()
        )

    def _loss_pickings_domain(self):
        return [("picking_type_id", "=", self.warehouse.loss_type_id.id)]

    def _get_loss_pickings(self):
        return (
            self.env["stock.picking"].search(self._loss_pickings_domain())
            - self.loss_pickings_before
        )

    def _get_quants_available_qty(self, line):
        quants_available_quantity = self.env["stock.quant"]._get_available_quantity(
            product_id=line.product_id,
            location_id=line.location_id,
            lot_id=line.lot_id,
            package_id=line.package_id,
            owner_id=line.owner_id,
        )
        return quants_available_quantity
