# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.stock_production_lot_traceability.tests.common import (
    CommonStockLotTraceabilityCase,
)


class TestStockLotTraceability(CommonStockLotTraceabilityCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner1 = cls.env.ref("base.res_partner_1")
        cls.partner2 = cls.env.ref("base.res_partner_2")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.location_customers = cls.env.ref("stock.stock_location_customers")
        cls._do_picking_out(cls.partner1, cls.product3, cls.product3_lot1, 2)
        cls._do_picking_out(cls.partner2, cls.product3, cls.product3_lot2, 2)

    @classmethod
    def _do_picking_out(cls, partner, product, lot, quantity, validate=True):
        picking = cls.env["stock.picking"].create(
            {
                "partner_id": partner.id,
                "picking_type_id": cls.picking_type_out.id,
                "location_id": cls.location_stock.id,
                "location_dest_id": cls.location_customers.id,
                "move_type": "direct",
            }
        )
        moves = cls._do_stock_move(
            product,
            lot,
            quantity,
            picking.location_id,
            picking.location_dest_id,
            validate=False,
        )
        moves.write({"picking_id": picking.id})
        moves.move_line_ids.write({"picking_id": picking.id})
        if validate:
            picking.action_confirm()
            picking.button_validate()
        return picking

    def _get_shipment_report_lines(self, lot):
        Wizard = self.env["stock.shipment.traceability.report.wizard"]
        wizard = Wizard.create({"lot_id": lot.id})
        res = wizard.confirm()
        self.assertIn("res_model", res)
        self.assertIn("domain", res)
        return self.env[res["res_model"]].search(res["domain"])

    def test_report_wizard_form_onchange(self):
        Wizard = self.env["stock.shipment.traceability.report.wizard"]
        with Form(Wizard) as form:
            form.lot_id = self.product1_lot1
            self.assertEqual(form.product_id, self.product1)

    def test_shipment_report(self):
        # Case 1: Deliveries involving product1_lot1
        lines = self._get_shipment_report_lines(self.product1_lot1)
        self.assertEqual(lines.partner_id, self.partner1)
        self.assertEqual(lines.product_id, self.product3)
        self.assertEqual(lines.lot_id, self.product3_lot1)
        # Case 1: Deliveries involving product1_lot1
        lines = self._get_shipment_report_lines(self.product1_lot2)
        self.assertEqual(lines.partner_id, self.partner2)
        self.assertEqual(lines.product_id, self.product3)
        self.assertEqual(lines.lot_id, self.product3_lot2)
