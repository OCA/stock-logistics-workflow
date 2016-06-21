# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    tracking_group_ids = fields.One2many(
        string='Tracking Groups',
        comodel_name='stock.picking.tracking.group',
        inverse_name='picking_id',
    )
