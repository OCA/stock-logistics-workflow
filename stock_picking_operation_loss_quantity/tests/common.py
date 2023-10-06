# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


class OperationLossQuantityCommon:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.quant_obj = cls.env["stock.quant"]

        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product loss quantity",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "Code product loss",
                "tracking": "lot",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product 2 loss quantity no tracking",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "Code product lot_loss no tracking 2",
                "tracking": "none",
            }
        )
        cls.product_3 = cls.env["product.product"].create(
            {
                "name": "Product 3 loss quantity no tracking",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "Code product lot_loss no tracking 3",
                "tracking": "none",
            }
        )
        wh = cls.env["stock.warehouse"].search([], limit=1)
        cls.location = wh.lot_stock_id

        cls.loc_customer = cls.env.ref("stock.stock_location_customers")

        cls.pick_type = cls.env.ref("stock.picking_type_out")
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
                "picking_type_id": cls.pick_type.id,
                "location_id": cls.location.id,
                "location_dest_id": cls.loc_customer.id,
            }
        )
        cls.move_1a = cls.env["stock.move"].create(
            {
                "picking_id": cls.picking_1.id,
                "name": "Test move 1a",
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_uom_qty": 6,
                "location_id": cls.location.id,
                "location_dest_id": cls.loc_customer.id,
                "date": "2018-01-01 00:00:00",
            }
        )
        cls.move_1a._action_confirm()
        cls.move_1b = cls.env["stock.move"].create(
            {
                "picking_id": cls.picking_1.id,
                "name": "Test move 1b",
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_uom_qty": 1,
                "location_id": cls.location.id,
                "location_dest_id": cls.loc_customer.id,
                "date": "2018-01-01 00:00:00",
            }
        )
        cls.move_1b._action_confirm()

        # Put product in stock
        # LotA: 3
        # LotB: 5
        cls._create_quantities(cls.product_1, 3.0, lot=cls.product_1_lotA)
        cls._create_quantities(cls.product_1, 5.0, lot=cls.product_1_lotB)

    @classmethod
    def initiate_values_no_tracking(cls):
        # Create picking 2
        cls.picking_2 = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.pick_type.id,
                "location_id": cls.location.id,
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
                "location_id": cls.location.id,
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
                "product_uom_qty": 1,
                "location_id": cls.location.id,
                "location_dest_id": cls.loc_customer.id,
                "date": "2018-01-01 00:00:00",
            }
        )
        cls.move_3._action_confirm()

        # Put product in stock
        # Product2: 3
        # Product3: 5
        cls._create_quantities(cls.product_2, 3.0)
        cls._create_quantities(cls.product_3, 5.0)

    @classmethod
    def _create_quantities(cls, product, quantity, location=None, lot=None):
        cls.quant_obj.with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "inventory_quantity": quantity,
                "location_id": location.id if location else cls.location.id,
                "lot_id": lot.id if lot else False,
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
