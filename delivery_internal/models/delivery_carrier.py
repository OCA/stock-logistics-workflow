# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(
        selection_add=[
            ('internal', 'Internal'),
        ],
    )
    internal_delivery_company_id = fields.Many2one(
        string='Delivery Company',
        comodel_name='res.company',
    )
    internal_delivery_stock_picking_type_id = fields.Many2one(
        string='Delivery Stock Picking Type',
        comodel_name='stock.picking.type',
    )
    internal_delivery_money_picking_type_id = fields.Many2one(
        string='Delivery Money Picking Type',
        comodel_name='stock.picking.type',
    )
