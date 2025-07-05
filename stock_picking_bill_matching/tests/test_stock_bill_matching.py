from odoo import fields
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestStockBillMatching(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner_a = cls.env["res.partner"].create({"name": "Test Vendor Partner"})
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Test Product A",
                "type": "product",
                "standard_price": 50.0,
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Test Product B",
                "type": "product",
                "standard_price": 100.0,
            }
        )

        # Get the default incoming picking type for the main company
        cls.picking_type_in = cls.env["stock.picking.type"].search(
            [
                ("code", "=", "incoming"),
                ("warehouse_id.company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )
        if not cls.picking_type_in:
            # If no default one, create one
            warehouse = cls.env["stock.warehouse"].search(
                [("company_id", "=", cls.env.company.id)], limit=1
            )
            if not warehouse:
                warehouse = cls.env["stock.warehouse"].create(
                    {"name": "Test WH", "code": "TWH", "company_id": cls.env.company.id}
                )
            cls.picking_type_in = cls.env["stock.picking.type"].create(
                {
                    "name": "Test Receipts",
                    "code": "incoming",
                    "warehouse_id": warehouse.id,
                }
            )

    def create_picking(self, products_info):
        """Helper to create and process an incoming picking."""
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner_a.id,
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.picking_type_in.default_location_dest_id.id,
            }
        )
        for product, qty in products_info:
            self.env["stock.move"].create(
                {
                    "name": product.name,
                    "product_id": product.id,
                    "product_uom_qty": qty,
                    "product_uom": product.uom_id.id,
                    "picking_id": picking.id,
                    "location_id": picking.location_id.id,
                    "location_dest_id": picking.location_dest_id.id,
                }
            )
        picking.action_confirm()
        picking.action_assign()
        for move in picking.move_lines:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        return picking

    def create_bill(self, products_info):
        """Helper to create a draft vendor bill."""
        bill = self.env["account.move"].create(
            {
                "partner_id": self.partner_a.id,
                "move_type": "in_invoice",
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "quantity": qty,
                            "price_unit": price,
                        },
                    )
                    for product, qty, price in products_info
                ],
            }
        )
        return bill

    # TODO finish
