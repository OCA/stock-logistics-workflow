# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestStockOwnerRestrictionMrp(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.location = cls.warehouse.lot_stock_id
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_mrp = cls.env["stock.picking.type"].search(
            [
                ("code", "=", "mrp_operation"),
                ("warehouse_id", "=", cls.warehouse.id),
            ],
            limit=1,
        )
        cls.owner = cls.env["res.partner"].create({"name": "Owner test"})
        cls.other_owner = cls.env["res.partner"].create({"name": "Another owner"})
        cls.component = cls.env["product.product"].create(
            {"name": "Component", "type": "consu", "is_storable": True}
        )
        cls.finished = cls.env["product.product"].create(
            {"name": "Finished", "type": "consu", "is_storable": True}
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.component.id, "product_qty": 1.0})
                ],
            }
        )

    def _stock(self, quantity, owner=None):
        return self.env["stock.quant"].create(
            {
                "product_id": self.component.id,
                "location_id": self.location.id,
                "quantity": quantity,
                "owner_id": owner.id if owner else False,
            }
        )

    def _production(self, quantity=10.0):
        production = self.env["mrp.production"].create(
            {
                "product_id": self.finished.id,
                "product_uom_id": self.finished.uom_id.id,
                "product_qty": quantity,
                "bom_id": self.bom.id,
                "picking_type_id": self.picking_type_mrp.id,
            }
        )
        production.action_confirm()
        return production

    def test_components_take_the_owner_the_order_delivers_to(self):
        """The raw material of an order has no picking to take a partner from,
        so it takes the one its order ends up delivering to.

        Without this it resolved to no partner at all, which under *Picking
        partner* does not mean "unrestricted" but "restricted to nobody": the
        order reserved nothing and manufacturing stopped with no explanation.
        """
        self.picking_type_mrp.owner_restriction = "picking_partner"
        self._stock(50.0, self.owner)
        self._stock(50.0, self.other_owner)
        production = self._production()
        delivery = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.location.id,
                "location_dest_id": self.customer_location.id,
                "owner_id": self.owner.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "delivery of the finished product",
                            "product_id": self.finished.id,
                            "product_uom_qty": 10.0,
                            "product_uom": self.finished.uom_id.id,
                            "location_id": self.location.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    )
                ],
            }
        )
        production.move_finished_ids.move_dest_ids = [(6, 0, delivery.move_ids.ids)]
        raw_move = production.move_raw_ids
        self.assertEqual(raw_move._get_owner_for_assign(), self.owner)
        production.action_assign()
        self.assertEqual(raw_move.quantity, 10.0)
        self.assertEqual(raw_move.move_line_ids.owner_id, self.owner)

    def test_finished_product_belongs_to_whoever_owned_the_components(self):
        """What is made out of a partner's goods belongs to that partner, so it
        carries the owner and is not valued."""
        self.picking_type_mrp.owner_restriction = "partner_or_unassigned"
        self._stock(100.0, self.owner)
        production = self._production()
        production.action_assign()
        production.qty_producing = 10.0
        production._set_qty_producing()
        self.assertEqual(production.move_raw_ids.move_line_ids.owner_id, self.owner)
        production.button_mark_done()
        finished_move = production.move_finished_ids
        self.assertEqual(finished_move.restrict_partner_id, self.owner)
        self.assertEqual(finished_move.move_line_ids.owner_id, self.owner)
        quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.finished.id),
                ("location_id", "child_of", self.location.id),
            ]
        )
        self.assertEqual(quant.owner_id, self.owner)

    def test_the_finished_product_of_own_components_is_untouched(self):
        """The ordinary case must go on exactly as before: no owner anywhere."""
        self.picking_type_mrp.owner_restriction = "partner_or_unassigned"
        self._stock(100.0)
        production = self._production()
        production.action_assign()
        production.qty_producing = 10.0
        production._set_qty_producing()
        production.button_mark_done()
        self.assertFalse(production.move_finished_ids.restrict_partner_id)
        self.assertFalse(production.move_finished_ids.move_line_ids.owner_id)

    def test_completing_with_own_stock_still_goes_to_the_partner(self):
        """*Picking partner or unassigned owner* is the one mode where mixing is
        the designed behaviour: it reserves from the partner and completes with
        unowned stock. What comes out goes to the partner, because the
        alternative is leaving their share of it at zero cost.
        """
        self.picking_type_mrp.owner_restriction = "partner_or_unassigned"
        self._stock(5.0, self.owner)
        self._stock(5.0)
        production = self._production()
        production.action_assign()
        production.qty_producing = 10.0
        production._set_qty_producing()
        self.assertEqual(len(production.move_raw_ids.move_line_ids), 2)
        production.button_mark_done()
        self.assertEqual(production.move_finished_ids.restrict_partner_id, self.owner)
        self.assertEqual(
            production.move_finished_ids.move_line_ids.owner_id, self.owner
        )

    def test_a_strict_partner_order_cannot_be_completed_with_own_stock(self):
        """Under *Picking partner* every component comes from that partner, so
        finding company stock among them is anomalous and has no answer."""
        self.picking_type_mrp.owner_restriction = "picking_partner"
        self._stock(5.0, self.owner)
        self._stock(5.0)
        production = self._production()
        production.move_raw_ids.move_line_ids.unlink()
        for quantity, owner in ((5.0, self.owner), (5.0, False)):
            self.env["stock.move.line"].create(
                {
                    "move_id": production.move_raw_ids.id,
                    "product_id": self.component.id,
                    "product_uom_id": self.component.uom_id.id,
                    "quantity": quantity,
                    "owner_id": owner.id if owner else False,
                    "location_id": self.location.id,
                    "location_dest_id": production.move_raw_ids.location_dest_id.id,
                    "picked": True,
                }
            )
        production.qty_producing = 10.0
        with self.assertRaisesRegex(UserError, "mixes components"):
            production.button_mark_done()

    def test_unassigned_owner_refuses_an_owned_component(self):
        """The restriction says no component may belong to anybody. If one does,
        something went around the reservation and blessing it here would hand
        the finished product to a partner nobody chose."""
        self.picking_type_mrp.owner_restriction = "unassigned_owner"
        self._stock(10.0, self.owner)
        production = self._production()
        production.move_raw_ids.move_line_ids.unlink()
        self.env["stock.move.line"].create(
            {
                "move_id": production.move_raw_ids.id,
                "product_id": self.component.id,
                "product_uom_id": self.component.uom_id.id,
                "quantity": 10.0,
                "owner_id": self.owner.id,
                "location_id": self.location.id,
                "location_dest_id": production.move_raw_ids.location_dest_id.id,
                "picked": True,
            }
        )
        production.qty_producing = 10.0
        with self.assertRaisesRegex(UserError, "unowned stock only"):
            production.button_mark_done()

    def test_two_owners_have_no_answer(self):
        self.picking_type_mrp.owner_restriction = "partner_or_unassigned"
        production = self._production()
        production.move_raw_ids.move_line_ids.unlink()
        for owner in (self.owner, self.other_owner):
            self._stock(5.0, owner)
            self.env["stock.move.line"].create(
                {
                    "move_id": production.move_raw_ids.id,
                    "product_id": self.component.id,
                    "product_uom_id": self.component.uom_id.id,
                    "quantity": 5.0,
                    "owner_id": owner.id,
                    "location_id": self.location.id,
                    "location_dest_id": production.move_raw_ids.location_dest_id.id,
                    "picked": True,
                }
            )
        production.qty_producing = 10.0
        with self.assertRaisesRegex(UserError, "more than one owner"):
            production.button_mark_done()
