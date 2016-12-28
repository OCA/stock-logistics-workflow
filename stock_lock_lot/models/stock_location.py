# -*- coding: utf-8 -*-
# © 2016 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class StockLocation(models.Model):

    _inherit = 'stock.location'

    allow_locked = fields.Boolean(string='Allow Locked')
