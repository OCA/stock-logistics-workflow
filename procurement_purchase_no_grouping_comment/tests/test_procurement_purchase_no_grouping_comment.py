# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class TestProcurementPurchaseNoGroupingComment(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Test vendor"})
        cls.customer = cls.env["res.partner"].create({"name": "Test customer"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "is_storable": True,
                "seller_ids": [(0, 0, {"partner_id": cls.vendor.id, "min_qty": 1.0})],
            }
        )
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.origin = "Test No Grouping Comment"
        cls.prev_orders = cls.env["purchase.order"].search(
            [("origin", "=", cls.origin)]
        )
        cls.buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.stock_rule = cls.buy_route.rule_ids[0]

    def _build_procurement(self, vendor_comment, qty=1.0):
        values = {
            # Must be a recordset, not an id: core's `_get_rule_domain` does
            # `values["company_id"].ids`. `ProcurementGroup.run()` would set it
            # that way, but we call `_get_rule` and `_run_buy` directly.
            "company_id": self.env.company,
            "date_planned": fields.Datetime.now(),
            "vendor_comment": vendor_comment,
        }
        procurement = self.env["procurement.group"].Procurement(
            self.product,
            qty,
            self.product.uom_id,
            self.location,
            False,
            self.origin,
            self.env.company,
            values,
        )
        rule = self.env["procurement.group"]._get_rule(
            procurement.product_id, procurement.location_id, procurement.values
        )
        return procurement, rule

    def _run_buy(self, *vendor_comments):
        """Run the given procurements within a single ``_run_buy`` batch."""
        self.stock_rule._run_buy(
            [self._build_procurement(comment) for comment in vendor_comments]
        )

    def _get_purchase_order(self):
        return self.env["purchase.order"].search(
            [("origin", "=", self.origin), ("id", "not in", self.prev_orders.ids)]
        )

    def test_distinct_comment_not_merged_in_batch(self):
        """Procurements of the same product with a distinct vendor comment must
        not be merged together, even when run in the same batch.
        """
        self._run_buy("Comment A", "Comment B")
        order = self._get_purchase_order()
        self.assertEqual(len(order), 1)
        self.assertEqual(len(order.order_line), 2)
        self.assertEqual(
            set(order.order_line.mapped("vendor_comment")), {"Comment A", "Comment B"}
        )

    def test_same_comment_merged_in_batch(self):
        """Sharing the vendor comment must not prevent the standard merge."""
        self._run_buy("Comment A", "Comment A")
        order = self._get_purchase_order()
        self.assertEqual(len(order), 1)
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.order_line.vendor_comment, "Comment A")
        self.assertEqual(order.order_line.product_qty, 2)

    def test_distinct_comment_not_merged_across_batches(self):
        """A distinct vendor comment must yield a new line on the existing order
        instead of being merged into the candidate one.
        """
        self._run_buy("Comment A")
        self._run_buy("Comment B")
        order = self._get_purchase_order()
        self.assertEqual(len(order), 1, "The existing purchase order must be reused")
        self.assertEqual(len(order.order_line), 2)
        self.assertEqual(
            set(order.order_line.mapped("vendor_comment")), {"Comment A", "Comment B"}
        )

    def test_same_comment_merged_across_batches(self):
        """An existing line with the same vendor comment must be found as a
        candidate and get its quantity increased.
        """
        self._run_buy("Comment A")
        self._run_buy("Comment A")
        order = self._get_purchase_order()
        self.assertEqual(len(order), 1)
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.order_line.product_qty, 2)

    def test_empty_comment_not_merged_with_commented_one(self):
        """An empty vendor comment is a grouping criterion on its own."""
        self._run_buy(False, "Comment A")
        order = self._get_purchase_order()
        self.assertEqual(len(order.order_line), 2)
        self.assertEqual(
            set(order.order_line.mapped("vendor_comment")), {False, "Comment A"}
        )

    def test_comment_propagated_to_stock_moves(self):
        """Confirming the order must carry each vendor comment over to its move,
        and moves with a distinct comment must stay unmerged.
        """
        self._run_buy("Comment A", "Comment B")
        order = self._get_purchase_order()
        order.button_confirm()
        moves = order.picking_ids.move_ids
        self.assertEqual(len(moves), 2)
        self.assertEqual(
            set(moves.mapped("vendor_comment")), {"Comment A", "Comment B"}
        )

    def test_sale_line_procurement_values(self):
        """The sale line must feed the vendor and the comment into the
        procurement values, which is what drives the whole no-grouping logic.
        """
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "vendor_id": self.vendor.id,
                            "vendor_comment": "Comment A",
                        },
                    )
                ],
            }
        )
        values = sale_order.order_line._prepare_procurement_values()
        self.assertEqual(values["vendor_id"], self.vendor.id)
        self.assertEqual(values["vendor_comment"], "Comment A")

    def test_stock_move_procurement_values(self):
        """A move must propagate its own vendor and comment downstream, so that
        chained (MTO) procurements keep the criterion.
        """
        move = self.env["stock.move"].create(
            {
                "name": "Test move",
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "product_uom": self.product.uom_id.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.location.id,
                "vendor_id": self.vendor.id,
                "vendor_comment": "Comment A",
            }
        )
        values = move._prepare_procurement_values()
        self.assertEqual(values["vendor_id"], self.vendor.id)
        self.assertEqual(values["vendor_comment"], "Comment A")

    def test_custom_move_fields_propagated_by_rule(self):
        """The rule must copy the vendor and the comment from the procurement
        values onto the move it generates.
        """
        values = {
            "company_id": self.env.company,
            "date_planned": fields.Datetime.now(),
            "vendor_id": self.vendor.id,
            "vendor_comment": "Comment A",
        }
        move_values = self.stock_rule._get_stock_move_values(
            self.product,
            1.0,
            self.product.uom_id,
            self.location,
            "Test move",
            self.origin,
            self.env.company,
            values,
        )
        self.assertEqual(move_values["vendor_id"], self.vendor.id)
        self.assertEqual(move_values["vendor_comment"], "Comment A")
