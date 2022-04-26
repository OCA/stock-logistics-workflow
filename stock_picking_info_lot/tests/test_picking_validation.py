from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPickingValidation(TransactionCase):
    def _create_picking(self, partner, p_type, src, dest):
        picking = (
            self.env["stock.picking"]
            .with_context(default_immediate_transfer=True)
            .create(
                {
                    "partner_id": partner.id,
                    "picking_type_id": p_type.id,
                    "location_id": src.id,
                    "location_dest_id": dest.id,
                }
            )
        )
        return picking

    def _create_move(self, product, src, dest, quantity=5.0, picking=None):
        return self.env["stock.move"].create(
            {
                "name": "/",
                "picking_id": picking.id if picking is not None else None,
                "product_id": product.id,
                "product_uom_qty": quantity,
                "quantity_done": quantity,
                "product_uom": product.uom_id.id,
                "location_id": src.id,
                "location_dest_id": dest.id,
            }
        )

    def setUp(self):
        super().setUp()

        suppliers_location = self.env.ref("stock.stock_location_suppliers")
        stock_location = self.env.ref("stock.stock_location_stock")
        customers_location = self.env.ref("stock.stock_location_customers")

        self.partner = self.env.ref("base.res_partner_2")
        self.product = self.env.ref("product.product_product_25")
        self.product.lot_info_usage = "required"
        self.replenishment = self._create_move(
            self.product, suppliers_location, stock_location, quantity=1
        )

        self.picking = self._create_picking(
            self.partner,
            self.env.ref("stock.picking_type_out"),
            stock_location,
            customers_location,
        )
        self.move = self._create_move(
            self.product,
            stock_location,
            customers_location,
            quantity=1,
            picking=self.picking,
        )
        self.picking.action_confirm()

    def test_picking_validation(self):
        with self.assertRaises(UserError):
            self.picking.button_validate()
