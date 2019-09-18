# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestWholeDropshipping(TransactionCase):

    def test_dropship_from_demo_data(self):
        sale = self.env.ref(
            "stock_dropshipping_whole_supplier.whole_dropship_sale")
        self._check_whole_dropship_from_sale(sale)

    def test_with_wood_corner_vendor(self):
        woodc = self.env.ref("base.res_partner_1")
        woodc.write({"allow_whole_order_dropshipping": True})
        sale = self.env["sale.order"].create({
            "partner_id": self.env.ref("base.res_partner_1").id,  # Deco addict
        })
        sale_line = self.env.ref(
            "stock_dropshipping_whole_supplier.whole_dropship_sale_line10")
        vals = sale_line._convert_to_write(sale_line.read()[0])
        ecom11 = self.env.ref("product.product_product_10")
        self._check_product_settings(woodc, ecom11)
        # We set it as dropship product
        ecom11.write({"route_ids": [
            (4, self.env.ref("stock_dropshipping.route_drop_shipping").id)]})
        self._create_sale_line(sale, vals, ecom11)
        furn_6666 = self.env.ref("product.product_product_25")
        self._check_product_settings(woodc, furn_6666)
        self._create_sale_line(sale, vals, furn_6666)
        self._check_whole_dropship_from_sale(sale)

    def _check_product_settings(self, vendor, product):
        """ Required hypothesis to have a correct execution """
        self.assertNotEqual(product.seller_ids, False)
        self.assertEqual(product.seller_ids[0].name, vendor)

    def _create_sale_line(self, sale, vals, product):
        vals["product_id"] = product.id
        vals["order_id"] = sale.id
        line = self.env['sale.order.line'].new(vals)
        line.product_id_change()
        values = line._convert_to_write(line._cache)
        self.env['sale.order.line'].create(values)

    def _check_whole_dropship_from_sale(self, sale):
        sale.action_confirm()
        sale_products = sale.order_line.mapped("product_id")
        po = self.env["purchase.order"].search([("origin", "=", sale.name)])
        purchase_products = po.order_line.mapped('product_id')
        self.assertEqual(sale_products, purchase_products)
        po.button_confirm()
        locations = po.picking_ids.move_ids_without_package.mapped(
            "location_dest_id")
        self.assertEqual(locations, self.env.ref(
            "stock.stock_location_customers"),
            "location_dest_id should be 'stock.stock_location_customers' "
            "like any destination dropship location")
