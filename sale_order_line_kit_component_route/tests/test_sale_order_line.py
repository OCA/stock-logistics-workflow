#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.mrp.tests.common import TestMrpCommon
from odoo.exceptions import UserError
from odoo.tests import Form


class TestSaleOrderLine (TestMrpCommon):

    def test_sale(self):
        """Sale a Kit, the routes of its components are executed."""
        # Arrange: Have a kit whose components have the MTO route
        bom = self.bom_2
        kit = bom.product_id
        component_1 = bom.bom_line_ids[0].product_id
        component_2 = bom.bom_line_ids[1].product_id
        routes = self.env.ref('stock.route_warehouse0_mto')
        (component_1 | component_2).update({
            'route_ids': routes,
        })

        # pre-condition
        self.assertEqual(bom.type, 'phantom')

        # Act
        sale_form = Form(self.env['sale.order'])
        sale_form.partner_id = self.env.ref('base.res_partner_12')
        with sale_form.order_line.new() as line:
            line.product_id = kit
        sale = sale_form.save()

        with self.assertRaises(UserError) as ue:
            sale.action_confirm()
        exc_message = ue.exception.args[0]

        # Assert: There are no procurement rules for the first component
        self.assertIn("No procurement rule found", exc_message)
        self.assertIn(component_1.name, exc_message)
