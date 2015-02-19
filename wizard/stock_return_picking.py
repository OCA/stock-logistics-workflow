# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.multi
    def _create_returns(self):
        result = super(StockReturnPicking, self)._create_returns()
        self._package_treat(self._context['active_id'])
        new_picking_id, pick_type_id = result
        self._package_treat(new_picking_id)
        return result

    @api.multi
    def _package_treat(self, picking_id):
        picking_obj = self.env['stock.picking']
        picking = picking_obj.browse(picking_id)
        packages = []
        for operation in picking.pack_operation_ids:
            if operation.result_package_id:
                packages.append(operation.result_package_id.id)
        picking.packages = [(6, 0, packages)]
