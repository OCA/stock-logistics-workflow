# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    tracking_group_ids = fields.One2many(
        string='Tracking Groups',
        comodel_name='stock.picking.tracking.group',
        inverse_name='picking_id',
    )
