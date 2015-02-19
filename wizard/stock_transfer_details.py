# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):
        result = super(StockTransferDetails, self).do_detailed_transfer()
        packages = []
        for operation in self.picking_id.pack_operation_ids:
            if operation.result_package_id:
                packages.append(operation.result_package_id.id)
        self.picking_id.packages = [(6, 0, packages)]
        return result
