# -*- coding: utf-8 -*-
# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    purchase_on_no_backorder = fields.Boolean(
        'Purchase on No Backorder',
        help='Requests quotation of cancelled stock picking on'
        ' no backorder reception.')
