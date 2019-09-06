# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestWholeDropshipping(TransactionCase):

    def test_dropship_all_furnitures(self):
        sale = self.env.ref(
            "stock_dropshipping_whole_supplier.whole_dropship_sale")
        sale.action_confirm()
        sale_products = sale.order_line.mapped("product_id")
        po = self.env["purchase.order"].search([("origin", "=", sale.name)])
        purchase_products = po.order_line.mapped('product_id')
        self.assertEqual(sale_products, purchase_products)
        po.button_confirm()
        locations = po.picking_ids.move_ids_without_package.mapped(
            "location_dest_id")
        self.assertEqual(locations, self.env.ref(
            "stock.stock_location_customers"))
