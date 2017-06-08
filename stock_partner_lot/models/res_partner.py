# -*- coding: utf-8 -*-

from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    quant_ids = fields.One2many('stock.quant', 'owner_id', string='Owned products')
