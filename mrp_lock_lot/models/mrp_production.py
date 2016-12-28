# -*- coding: utf-8 -*-
# © 2016 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.model
    def _calculate_qty(self, production, product_qty=0.0):
        lines = super(MrpProduction, self)._calculate_qty(
            production, product_qty=product_qty)
        allow = production.product_id.property_stock_production.allow_locked
        for line in lines:
            line['allow_locked'] = allow
        return lines
