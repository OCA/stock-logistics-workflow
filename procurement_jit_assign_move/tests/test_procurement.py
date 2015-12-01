# -*- coding: utf-8 -*-
# © 2015 Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp import fields


class ProcurementTest(TransactionCase):

    def test_procurement_jit_again(self):
        values = {'company_id': self.env.ref('base.main_company').id,
                  'date_planned': fields.Datetime.now(),
                  'name': 'SOME/TEST/0001',
                  'product_id': self.env.ref('product.product_product_16').id,
                  'product_qty': 4,
                  'product_uom': self.env.ref('product.product_uom_unit').id,
                  'product_uos_qty': 0,
                  }
        proc = self.env['procurement.order'].create(values)
        self.assertEqual(proc.state, 'exception')
