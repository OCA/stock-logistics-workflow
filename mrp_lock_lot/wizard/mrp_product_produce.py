# -*- coding: utf-8 -*-
# © 2016 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class MrpProductProduceLine(models.TransientModel):

    _inherit = 'mrp.product.produce.line'

    allow_locked = fields.Boolean(string='Allow Locked')


class MrpProductProduce(models.TransientModel):

    _inherit = 'mrp.product.produce'

    allow_locked = fields.Boolean(
        string='Allow locked', default=lambda self: self._get_allow_locked())

    @api.model
    def _get_allow_locked(self):
        prod = self.env['mrp.production'].browse(
            self.env.context.get('active_id'))
        return prod.location_dest_id.allow_locked
