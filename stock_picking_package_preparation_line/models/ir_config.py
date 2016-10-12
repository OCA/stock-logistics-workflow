# -*- coding: utf-8 -*-
# © 2015 - Francesco Apruzzese <f.apruzzese@apuliasoftware.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    default_picking_type_for_package_preparation_id = fields.Many2one(
        'stock.picking.type',
        string='Default Picking Type used in package preparation')


class StockPickingPackagePreparationLineSettings(models.TransientModel):

    _inherit = 'stock.config.settings'

    default_picking_type_for_package_preparation_id = fields.Many2one(
        'stock.picking.type',
        related='company_id.default_picking_type_for_package_preparation_id')

    def default_get(self, cr, uid, fields, context=None):
        res = super(StockPickingPackagePreparationLineSettings,
                    self).default_get(cr, uid, fields, context)
        if res:
            company = self.pool['res.users'].browse(cr, uid, uid,
                                                    context).company_id
            res['default_picking_type_for_package_preparation_id'] = \
                company.default_picking_type_for_package_preparation_id.id \
                if company.default_picking_type_for_package_preparation_id \
                else False
        return res
