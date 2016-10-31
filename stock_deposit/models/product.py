# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.tools.float_utils import float_round
from openerp.models import expression
from openerp.tools.safe_eval import safe_eval


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def _compute_deposit_available(self):
        for template in self:
            template.deposit_available = sum(
                template.mapped('product_variant_ids.deposit_available')
            )

    deposit_available = fields.Float(
        compute='_compute_deposit_available',
        string='Deposit Qty Available'
    )

    def _exclude_deposit_location_action(self, res_action):
        ctx = safe_eval(res_action['context'])
        ctx.update({'search_default_deposit_loc_exclude': 1})
        res_action['context'] = ctx
        return res_action

    def _only_deposit_location_action(self, res_action):
        ctx = safe_eval(res_action['context'])
        ctx.update({'search_default_deposit_loc': 1})
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

    @api.multi
    def deposit_action_open_quants(self):
        res = super(ProductTemplate, self).action_open_quants()
        return self._only_deposit_location_action(res)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _compute_deposit_available(self):
        domain_quant_loc = self.with_context(
            deposit_locations=True)._get_domain_locations()[0]
        domain_quant = domain_quant_loc + [('product_id', 'in', self.ids)]
        quants = self.env['stock.quant'].read_group(
            domain_quant, ['product_id', 'qty'], ['product_id'])
        quants = dict(map(lambda x: (x['product_id'][0], x['qty']), quants))
        for product in self:
            product.deposit_available = float_round(
                quants.get(product.id, 0.0),
                precision_rounding=product.uom_id.rounding)

    deposit_available = fields.Float(
        compute='_compute_deposit_available',
        string='Deposit Qty Available'
    )

    @api.multi
    def _get_domain_locations(self):
        domains = super(ProductProduct, self)._get_domain_locations()
        deposit_locations = self.env.context.get('deposit_locations', False)
        if domains:
            quant_domain = expression.AND([[
                ('location_id.deposit_location', '=', deposit_locations),
            ], domains[0]])
            return quant_domain, domains[1], domains[2]
        return domains
