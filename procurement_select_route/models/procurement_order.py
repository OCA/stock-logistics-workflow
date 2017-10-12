# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    product_route_id = fields.Many2one(
        'stock.location.route', 'Product Route')

    product_categ_id = fields.Many2one(
        'product.category', 'Product Category', related='product_id.categ_id')

    @api.multi
    def run(self, autocommit=False):
        procurements_to_run = self.env['procurement.order']
        for procurement in self:
            if procurement.rule_id or len(procurement.route_ids) == 1:
                procurements_to_run |= procurement
                continue

            if procurement.product_route_id:
                procurement.route_ids = procurement.product_route_id
                procurements_to_run |= procurement
                continue

            product = procurement.product_id
            routes = product.route_ids | product.categ_id.route_ids

            if len(set(routes.ids)) > 1:
                procurement.message_post(body=_(
                    "The product %s has more than one possible "
                    "procurement route. Please specify the route "
                    "to use in the field 'Product Route'.") %
                    product.name)
                procurement.state = 'exception'
            else:
                procurements_to_run |= procurement

        if procurements_to_run:
            return super(ProcurementOrder, procurements_to_run).run(
                autocommit=autocommit)

        return True
