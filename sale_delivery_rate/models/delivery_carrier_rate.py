# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class DeliveryCarrierRate(models.Model):
    _name = 'delivery.carrier.rate'
    _description = 'Delivery Carrier Rate'
    _inherit = 'stock.picking.rate'

    picking_id = fields.Many2one(required=False)
    sale_order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        required=True,
    )

    @api.multi
    def generate_equiv_picking_rates(self, stock_picking):
        stock_picking.ensure_one()
        recordset_data = self.copy_data()

        for record_data in recordset_data:
            del record_data['sale_order_id']
            record_data['picking_id'] = stock_picking.id
            self.env['stock.picking.rate'].create(record_data)
