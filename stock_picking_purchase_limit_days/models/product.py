# Copyright 2021 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, datetime
from dateutil.relativedelta import relativedelta 
from odoo import models, fields, api, _


class Product(models.Model):
    _inherit = "product.product"

    def _product_available(self, field_names=None, arg=False):
        if self.env.context.get('purchase_limit_days'):
            limited_qties = super(Product, self)._product_available(
                field_names=field_names, arg=arg)
            unlimited_qties = super(Product, self).with_context(
                to_date=False, purchase_limit_days=False)._product_available(
                    field_names=field_names, arg=arg)
            res = {}
            for product_id, qties in limited_qties.items():
                incoming_qty = unlimited_qties[product_id]['incoming_qty']
                virtual_qty = (qties['qty_available']
                               + incoming_qty - qties['outgoing_qty'])
                res[product_id] = {
                    'qty_available': qties['qty_available'],
                    'incoming_qty': incoming_qty,
                    'outgoing_qty': qties['outgoing_qty'],
                    'virtual_available': virtual_qty,
                }
        else:
            res = super(Product, self)._product_available(
                field_names=field_names, arg=arg)

        return res
