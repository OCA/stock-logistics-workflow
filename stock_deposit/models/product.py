# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.tools.safe_eval import safe_eval as eval


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def _compute_deposit_available(self):
        for product in self:
            product.deposit_available = product.with_context(
                deposit_locations=True).qty_available

    deposit_available = fields.Float(
        compute='_compute_deposit_available',
        string='Deposit Qty Available'
    )

    def _exclude_deposit_location_action(self, res_action):
        ctx = eval(res_action['context'])
        ctx.update({'search_default_deposit_loc_exclude': 1})
        res_action['context'] = ctx
        return res_action

    @api.multi
    def action_view_stock_moves(self):
        res = super(ProductTemplate, self).action_view_stock_moves()
        return self._exclude_deposit_location_action(res)

    @api.multi
    def action_open_quants(self):
        res = super(ProductTemplate, self).action_open_quants()
        return self._exclude_deposit_location_action(res)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _compute_deposit_available(self):
        for product in self:
            product.deposit_available = product.with_context(
                deposit_locations=True).qty_available

    deposit_available = fields.Float(
        compute='_compute_deposit_available',
        string='Deposit Qty Available'
    )

    @api.multi
    def _get_domain_locations(self):
        domain = super(ProductProduct, self)._get_domain_locations()
        deposit_locations = self.env.context.get('deposit_locations', False)
        if domain:
            domain[0].insert(
                0, ('location_id.deposit_location', '=', deposit_locations)
            )
            domain[0].insert(0, '&')
        return domain
