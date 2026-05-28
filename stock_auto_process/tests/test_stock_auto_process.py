# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError
from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestStockAutoProcess(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "product"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_out = cls.warehouse.out_type_id
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_customer = cls.env.ref("stock.stock_location_customers")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.location_stock, 100.0
        )

    def _create_picking(self, qty=5.0):
        return self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.location_stock.id,
                "location_dest_id": self.location_customer.id,
                "partner_id": self.partner.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": qty,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.location_stock.id,
                            "location_dest_id": self.location_customer.id,
                        }
                    )
                ],
            }
        )

    def _create_rule(self, **vals):
        defaults = {
            "name": "Test rule",
            "picking_type_ids": [Command.set([self.picking_type_out.id])],
            "do_confirm": True,
            "do_assign": True,
            "do_validate": True,
        }
        defaults.update(vals)
        return self.env["stock.auto.process.rule"].create(defaults)

    def test_full_pipeline_confirms_assigns_and_validates(self):
        rule = self._create_rule()
        picking = self._create_picking()
        self.env["automatic.process.job"]._process_rule(rule)
        self.assertEqual(picking.state, "done")

    def test_partial_picking_validated_with_backorder(self):
        rule = self._create_rule(create_backorder=True)
        picking = self._create_picking(qty=200.0)
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(picking.move_ids.state, "partially_available")
        self.env["automatic.process.job"]._process_rule(rule)
        self.assertEqual(picking.state, "done")
        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", picking.id)]
        )
        self.assertTrue(backorder)

    def test_partial_picking_validated_without_backorder(self):
        rule = self._create_rule(create_backorder=False)
        picking = self._create_picking(qty=200.0)
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(picking.move_ids.state, "partially_available")
        self.env["automatic.process.job"]._process_rule(rule)
        self.assertEqual(picking.state, "done")
        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", picking.id)]
        )
        self.assertFalse(backorder)

    def test_picking_type_filter_excludes_other_types(self):
        other_type = self.warehouse.in_type_id
        rule = self._create_rule(picking_type_ids=[Command.set([other_type.id])])
        picking = self._create_picking()
        self.env["automatic.process.job"]._process_rule(rule)
        self.assertEqual(picking.state, "draft")

    def test_broken_rule_does_not_poison_other_rules(self):
        self._create_rule(name="Broken", domain="not a domain")
        self._create_rule(name="Good")
        picking = self._create_picking()
        # cron entry point iterates all rules; the broken rule must not abort
        # processing of the good one.
        self.env["automatic.process.job"].run()
        self.assertEqual(picking.state, "done")

    def test_stock_user_can_read(self):
        rule = self._create_rule()
        stock_user = self.env["res.users"].create(
            {
                "name": "Stock User",
                "login": "stock_user",
                "groups_id": [Command.set([self.env.ref("stock.group_stock_user").id])],
            }
        )
        rule.with_user(stock_user).read(["name"])

    def test_stock_user_cannot_create(self):
        stock_user = self.env["res.users"].create(
            {
                "name": "Stock User",
                "login": "stock_user_create",
                "groups_id": [Command.set([self.env.ref("stock.group_stock_user").id])],
            }
        )
        Rule = self.env["stock.auto.process.rule"]
        with self.assertRaises(AccessError):
            Rule.with_user(stock_user).create({"name": "Blocked"})

    def test_auto_process_user_has_full_access(self):
        auto_process_user = self.env["res.users"].create(
            {
                "name": "Auto Process User",
                "login": "auto_process_user",
                "groups_id": [
                    Command.set(
                        [
                            self.env.ref("stock.group_stock_user").id,
                            self.env.ref(
                                "stock_auto_process.group_stock_auto_process"
                            ).id,
                        ]
                    )
                ],
            }
        )
        Rule = self.env["stock.auto.process.rule"]
        rule = Rule.with_user(auto_process_user).create({"name": "New Rule"})
        rule.write({"name": "Updated Rule"})
        rule.unlink()
