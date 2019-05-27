# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    weight_uom_id = fields.Many2one(required=False)
