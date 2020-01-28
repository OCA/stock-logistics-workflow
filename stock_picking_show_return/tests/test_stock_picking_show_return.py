# Copyright 2014-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestStockPickingShowReturn(common.TransactionCase):
    def setUp(self):
        super(TestStockPickingShowReturn, self).setUp()
        self.product = self.env["product.product"].create({"name": "Test product"})
        picking_type = self.env.ref("stock.picking_type_internal")
        self.picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

    def test_returned_ids_field(self):
        self.picking.action_assign()
        self.picking.move_line_ids.qty_done = 1
        self.picking.action_done()
        wizard = (
            self.env["stock.return.picking"]
            .with_context(active_ids=self.picking.ids, active_id=self.picking.id)
            .create({})
        )
        wizard.create_returns()
        self.assertTrue(self.picking.returned_ids)
