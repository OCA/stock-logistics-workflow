# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import exceptions
from odoo.tests.common import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestMergeWizard(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.wh = wh = cls.env.ref("stock.warehouse0")
        wh.group_shippings = True
        cls.product = cls.env.ref("product.product_product_4")
        cls.products = (
            cls.product
            | cls.env.ref("product.product_product_9")
            | cls.env.ref("product.product_product_20")
        )

        cls.carrier1 = cls.env["delivery.carrier"].create(
            {
                "name": "My Test Carrier",
                "product_id": cls.env.ref("delivery.product_product_delivery").id,
            }
        )
        cls.carrier2 = cls.env["delivery.carrier"].create(
            {
                "name": "My Other Test Carrier",
                "product_id": cls.env.ref("delivery.product_product_delivery").id,
            }
        )
        cls.partner1 = cls.env["res.partner"].create({"name": "Test Merge 1"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Test Merge 2"})

        cls.no_partner = cls.env["res.partner"].browse()
        cls.no_carrier = cls.env["delivery.carrier"].browse()

        cls.all_pickings_partner1 = cls.env["stock.picking"]
        for i, prod in enumerate(cls.products, 1):
            group = cls._create_proc_group(partner_id=cls.partner1.id)
            move = cls._create_move(product=prod, group_id=group.id)
            move._assign_picking()
            cls.all_pickings_partner1 |= move.picking_id
            setattr(cls, "pick_p1_%d" % i, move.picking_id)
        cls.all_pickings_partner1.write({"partner_id": cls.partner1.id})

        cls.all_pickings_partner2 = cls.env["stock.picking"]
        for i, prod in enumerate(cls.products, 1):
            group = cls._create_proc_group(partner_id=cls.partner2.id)
            move = cls._create_move(product=prod, group_id=group.id)
            move._assign_picking()
            cls.all_pickings_partner2 |= move.picking_id
            setattr(cls, "pick_p2_%d" % i, move.picking_id)
        cls.all_pickings_partner2.write({"partner_id": cls.partner2.id})

    @classmethod
    def _create_move(cls, product=None, **kw):
        product = product or cls.product
        vals = {
            "name": product.name,
            "product_id": product.id,
            "product_uom_qty": 1,
            "product_uom": product.uom_id.id,
            "location_id": cls.wh.lot_stock_id.id,
            "location_dest_id": cls.wh.wh_output_stock_loc_id.id,
            "state": "confirmed",
            "picking_type_id": cls.wh.out_type_id.id,
        }
        vals.update(kw)
        move = cls.env["stock.move"].create(vals)
        return move

    @classmethod
    def _create_proc_group(cls, **kw):
        vals = {"name": "Procure TEST"}
        vals.update(kw)
        return cls.env["procurement.group"].create(vals)

    def _get_wizard(self, picking_ids):
        return (
            self.env["stock.picking.merge"]
            .with_context(active_ids=picking_ids)
            .create({})
        )

    def test_wiz_has_todo(self):
        # All pickings belong to the same partner
        wiz = self._get_wizard(self.all_pickings_partner1.ids)
        valid_expected = self.all_pickings_partner1
        self.assertEqual(wiz.selected_picking_ids, valid_expected)
        self.assertEqual(wiz.valid_picking_ids, valid_expected)
        self.assertFalse(wiz.discarded_picking_ids)
        self.assertFalse(wiz.nothing_todo)
        info = wiz._get_grouping_info()
        self.assertEqual(
            info,
            {
                "grouping_forecast": [
                    {
                        "carrier": self.no_carrier,
                        "partner": self.partner1,
                        "pickings": tuple([x for x in valid_expected]),
                        "has_todo": True,
                    }
                ],
                "discarded_pickings": wiz.discarded_picking_ids,
                "something_todo": True,
            },
        )
        all_moves = self.all_pickings_partner1.move_lines
        # merge and ensure we are left w/ one picking only
        wiz.action_merge()
        remaining_pickings = all_moves.mapped("picking_id")
        self.assertEqual(len(remaining_pickings), 1)
        self.assertRecordValues(
            self.all_pickings_partner1 - remaining_pickings,
            [{"state": "cancel", "canceled_by_merge": True}] * 2,
        )

    def test_wiz_discarded(self):
        # cancel a picking and ensure it's skipped
        self.pick_p1_1.action_cancel()
        wiz = self._get_wizard(self.all_pickings_partner1.ids)
        valid_expected = self.all_pickings_partner1 - self.pick_p1_1
        self.assertEqual(wiz.valid_picking_ids, valid_expected)
        self.assertEqual(wiz.discarded_picking_ids, self.pick_p1_1)
        self.assertFalse(wiz.nothing_todo)
        info = wiz._get_grouping_info()
        self.assertEqual(
            info,
            {
                "grouping_forecast": [
                    {
                        "carrier": self.no_carrier,
                        "partner": self.partner1,
                        "pickings": tuple([x for x in valid_expected]),
                        "has_todo": True,
                    }
                ],
                "discarded_pickings": wiz.discarded_picking_ids,
                "something_todo": True,
            },
        )
        self.pick_p1_2.printed = True
        wiz._compute_pickings()
        valid_expected = self.all_pickings_partner1 - self.pick_p1_1 - self.pick_p1_2
        self.assertEqual(
            wiz.valid_picking_ids, valid_expected,
        )
        self.assertEqual(wiz.discarded_picking_ids, self.pick_p1_1 + self.pick_p1_2)
        # Only one picking left, nothing to do
        self.assertTrue(wiz.nothing_todo)
        info = wiz._get_grouping_info()
        self.assertEqual(
            info,
            {
                "grouping_forecast": [
                    {
                        "carrier": self.no_carrier,
                        "partner": self.partner1,
                        "pickings": tuple([x for x in valid_expected]),
                        "has_todo": False,
                    }
                ],
                "discarded_pickings": wiz.discarded_picking_ids,
                "something_todo": False,
            },
        )
        message = "No picking can be merged!"
        with self.assertRaisesRegex(exceptions.UserError, message):
            wiz.action_merge()

    def test_wiz_has_todo_mixed_partner(self):
        all_pickings = self.all_pickings_partner1 + self.all_pickings_partner2
        wiz = self._get_wizard(all_pickings.ids)
        valid_expected = all_pickings
        self.assertEqual(wiz.selected_picking_ids, valid_expected)
        self.assertEqual(wiz.valid_picking_ids, valid_expected)
        self.assertFalse(wiz.discarded_picking_ids)
        self.assertFalse(wiz.nothing_todo)
        info = wiz._get_grouping_info()
        self.assertEqual(
            info,
            {
                "grouping_forecast": [
                    {
                        "carrier": self.no_carrier,
                        "partner": self.partner1,
                        "pickings": tuple([x for x in self.all_pickings_partner1]),
                        "has_todo": True,
                    },
                    {
                        "carrier": self.no_carrier,
                        "partner": self.partner2,
                        "pickings": tuple([x for x in self.all_pickings_partner2]),
                        "has_todo": True,
                    },
                ],
                "discarded_pickings": wiz.discarded_picking_ids,
                "something_todo": True,
            },
        )
        all_moves = all_pickings.move_lines
        # merge and ensure we are left w/ one picking only
        wiz.action_merge()
        remaining_pickings = all_moves.mapped("picking_id")
        self.assertEqual(len(remaining_pickings), 2)
        self.assertRecordValues(
            all_pickings - remaining_pickings,
            [{"state": "cancel", "canceled_by_merge": True}] * 4,
        )

    def test_wiz_has_todo_mixed_partner_mixed_carrier(self):
        self.all_pickings_partner1[0].carrier_id = self.carrier1
        self.all_pickings_partner1[1].carrier_id = self.carrier2
        self.all_pickings_partner1[2].carrier_id = self.carrier2
        self.all_pickings_partner1[0].move_lines.group_id.carrier_id = self.carrier1
        self.all_pickings_partner1[1].move_lines.group_id.carrier_id = self.carrier2
        self.all_pickings_partner1[2].move_lines.group_id.carrier_id = self.carrier2

        self.all_pickings_partner2[0].carrier_id = self.carrier1
        self.all_pickings_partner2[1].carrier_id = self.carrier2
        self.all_pickings_partner2[2].carrier_id = self.carrier1
        self.all_pickings_partner2[0].move_lines.group_id.carrier_id = self.carrier1
        self.all_pickings_partner2[1].move_lines.group_id.carrier_id = self.carrier2
        self.all_pickings_partner2[2].move_lines.group_id.carrier_id = self.carrier1

        all_pickings = self.all_pickings_partner1 + self.all_pickings_partner2
        wiz = self._get_wizard(all_pickings.ids)
        valid_expected = all_pickings
        self.assertEqual(wiz.selected_picking_ids, valid_expected)
        self.assertEqual(wiz.valid_picking_ids, valid_expected)
        self.assertFalse(wiz.discarded_picking_ids)
        self.assertFalse(wiz.nothing_todo)
        info = wiz._get_grouping_info()
        self.assertEqual(
            info,
            {
                "grouping_forecast": [
                    {
                        "carrier": self.carrier1,
                        "partner": self.partner1,
                        "pickings": tuple([x for x in self.all_pickings_partner1[:1]]),
                        # Only one picking, nothing to do
                        "has_todo": False,
                    },
                    {
                        "carrier": self.carrier2,
                        "partner": self.partner1,
                        "pickings": tuple([x for x in self.all_pickings_partner1[1:]]),
                        "has_todo": True,
                    },
                    {
                        "carrier": self.carrier1,
                        "partner": self.partner2,
                        "pickings": tuple(
                            [
                                x
                                for x in self.all_pickings_partner2
                                - self.all_pickings_partner2[1]
                            ]
                        ),
                        "has_todo": True,
                    },
                    {
                        "carrier": self.carrier2,
                        "partner": self.partner2,
                        "pickings": tuple([x for x in self.all_pickings_partner2[1:2]]),
                        # Only one picking, nothing to do
                        "has_todo": False,
                    },
                ],
                "discarded_pickings": wiz.discarded_picking_ids,
                "something_todo": True,
            },
        )
        all_moves = all_pickings.move_lines
        # merge and ensure we are left w/ one picking only
        wiz.action_merge()
        remaining_pickings = all_moves.mapped("picking_id")
        self.assertEqual(len(remaining_pickings), 4)
        self.assertRecordValues(
            all_pickings - remaining_pickings,
            [{"state": "cancel", "canceled_by_merge": True}] * 2,
        )
