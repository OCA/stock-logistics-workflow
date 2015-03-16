# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api
from datetime import datetime


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):
        result = super(StockTransferDetails, self).do_detailed_transfer()
        self.picking_id._catch_operations()
        return result

    @api.one
    def do_save_for_later(self):
        operation_obj = self.env['stock.pack.operation']
        # Create new and update existing pack operations
        for lstits in [self.item_ids, self.packop_ids]:
            for prod in lstits:
                pack_datas = {
                    'product_id': prod.product_id.id,
                    'product_uom_id': prod.product_uom_id.id,
                    'product_qty': prod.quantity,
                    'package_id': prod.package_id.id,
                    'lot_id': prod.lot_id.id,
                    'location_id': prod.sourceloc_id.id,
                    'location_dest_id': prod.destinationloc_id.id,
                    'result_package_id': prod.result_package_id.id,
                    'date': prod.date if prod.date else datetime.now(),
                    'owner_id': prod.owner_id.id,
                }
                if prod.packop_id:
                    if prod.packop_id.product_qty != prod.quantity:
                        qty = prod.packop_id.product_qty - prod.quantity
                        prod.packop_id.write({'product_qty': qty})
                        pack_datas['picking_id'] = self.picking_id.id
                        operation_obj.create(pack_datas)
                    else:
                        prod.packop_id.write(pack_datas)
        self.picking_id._catch_operations()
        return True
