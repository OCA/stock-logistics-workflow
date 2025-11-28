# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class StockScrap(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product A",
                "is_storable": True,
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )

        icp_sudo = cls.env["ir.config_parameter"].sudo()
        icp_sudo.set_param("scrap_order.scrap_reason_required", "False")

    def test_scrap_1(self):
        """Check the created stock move and the impact on quants when we scrap a
        storable product.
        """
        scrap_form = Form(self.env["stock.scrap"])
        scrap_form.product_id = self.product
        scrap_form.scrap_qty = 1
        self.assertFalse(scrap_form.scrap_reason_required)
        # Save successfully
        scrap = scrap_form.save()
        icp_sudo = self.env["ir.config_parameter"].sudo()
        icp_sudo.set_param("scrap_order.scrap_reason_required", "True")
        scrap_form2 = Form(scrap)
        self.assertTrue(scrap_form2.scrap_reason_required)
