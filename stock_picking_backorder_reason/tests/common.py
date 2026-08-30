# Copyright 2017 Camptocamp SA
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)


class TestPickingBackorder:

    _flow = None  # This will mention the actual flow (purchase, sale)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product_model = cls.env["product.product"]
        cls.partner_model = cls.env["res.partner"]
        cls.location_model = cls.env["stock.location"]
        cls.stock_picking_model = cls.env["stock.picking"]
        cls.stock_picking_type_model = cls.env["stock.picking.type"]
        cls.backorder_reason_model = cls.env["stock.backorder.reason"]
        cls.backorder_choice_model = cls.env["stock.backorder.reason.choice"]
        cls.backorder_confirmation_model = cls.env["stock.backorder.confirmation"]

        cls.product = cls.product_model.create(
            {
                "name": "Unittest P1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )

        cls.partner = cls.partner_model.create(
            {
                "name": "Unittest supplier",
                "sale_reason_backorder_strategy": "cancel",
                "ref": "123321",
            }
        )

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.output_location = cls.env.ref("stock.stock_location_output")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")

        cls.picking_type_in.write(
            {
                "backorder_reason": True,
                "backorder_reason_purchase": True,
            }
        )

        cls.picking_type_out.write(
            {
                "backorder_reason": True,
                "backorder_reason_sale": True,
            }
        )

        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.product.id,
                "inventory_quantity": 10.0,
                "location_id": cls.stock_location.id,
            }
        )._apply_inventory()

        # Define behaviour global variables
        cls.backorder_action = "create"
        cls.purchase_backorder = "create"
        cls.sale_backorder = "create"

        cls._create_backorder_reason()

    @classmethod
    def _create_picking(cls):
        if cls._flow == "purchase":
            picking_type = cls.picking_type_in.id
            location_id = cls.supplier_location.id
            location_dest_id = cls.stock_location.id
        elif cls._flow == "sale":
            picking_type = cls.picking_type_out.id
            location_id = cls.stock_location.id
            location_dest_id = cls.customer_location.id
        else:
            return

        # Create IN picking
        cls.picking = cls.stock_picking_model.create(
            {
                "picking_type_id": picking_type,
                "location_id": location_id,
                "location_dest_id": location_dest_id,
                "partner_id": cls.partner.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "a move",
                            "product_id": cls.product.id,
                            "product_uom_qty": 10,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": location_id,
                            "location_dest_id": location_dest_id,
                        },
                    )
                ],
            }
        )

        # Transfer picking partially
        cls.picking.action_confirm()
        cls.picking.action_assign()
        move_lines = cls.picking.move_line_ids
        move_lines.write({"qty_done": 3})

    @classmethod
    def _create_backorder_reason(cls):
        # Define backorder reason
        cls.backorder_reason = cls.backorder_reason_model.create(
            {
                "name": "Unittest backorder",
                "backorder_action_to_do": cls.backorder_action,
            }
        )

    def _check_backorder_behavior(self):
        # Here we define the behaviors for the different strategies and check
        # if everything is done in the expected way

        # Define the backorder behavior on partner
        self.partner.purchase_reason_backorder_strategy = self.purchase_backorder
        self.partner.sale_reason_backorder_strategy = self.sale_backorder

        # Change the behaviour depending on unit test
        self.backorder_reason.write({"backorder_action_to_do": self.backorder_action})

        result = self.picking.button_validate()

        # Check that the transfer action return the good wizard
        self.assertEqual(result["res_model"], "stock.backorder.reason.choice")

        # Create backorder choice wizard and execute it
        wizard = self.backorder_choice_model.with_context(**result["context"]).create(
            {"reason_id": self.backorder_reason.id}
        )
        result = wizard.apply()

        if not self.backorder_action:
            # We are in the case the action should come from the picking type
            # and let the core feature happen
            self.assertTrue(result)
            self.assertEqual("stock.backorder.confirmation", result.get("res_model"))
            return

        # Search created backorder
        self.backorder = self.stock_picking_model.search(
            [("backorder_id", "=", self.picking.id)]
        )

        partner_option_create = (
            self.purchase_backorder == "create"
            if self._flow == "purchase"
            else self.sale_backorder == "create"
        )

        keep_backorder = self.backorder_action == "create" or (
            self.backorder_action == "use_partner_option" and partner_option_create
        )

        # Check picking chatter has the backorder reason
        message = self.picking.message_ids.filtered(
            lambda message: self.backorder_reason.name in message.body
        )
        self.assertTrue(message)

        # Check picking values
        if keep_backorder:
            self.assertEqual(len(self.picking.move_ids), 1)
            self.assertEqual(self.picking.move_ids.product_id, self.product)
            self.assertEqual(self.picking.move_ids.product_uom_qty, 3)
            self.assertEqual(self.picking.move_ids.state, "done")
            self.assertEqual(self.picking.state, "done")
            # Check backorder values
            self.assertEqual(len(self.backorder), 1)
            self.assertEqual(self.backorder.move_ids.product_uom_qty, 7)
        else:
            self.assertEqual(len(self.picking.move_ids), 2)
            cancel_moves = self.picking.move_ids.filtered(
                lambda move: move.state == "cancel"
            )
            self.assertEqual(len(cancel_moves), 1)
            moves = self.picking.move_ids - cancel_moves
            self.assertEqual(len(moves), 1)
            self.assertFalse(self.backorder)
