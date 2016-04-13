# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api
from datetime import datetime


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.model
    def default_get(self, fields):
        picking = self.env['stock.picking'].browse(
            self.env.context.get('active_id'))
        if picking.pack_operation_ids:
            picking.create_all_move_packages()
        return super(StockTransferDetails, self).default_get(fields)

    @api.multi
    def do_save_for_later(self):
        self.ensure_one()
        operation_obj = self.env['stock.pack.operation'].with_context(
            no_recompute=True)
        self.picking_id.pack_operation_ids.unlink()
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
                    prod.packop_id.with_context(no_recompute=True).write(
                        pack_datas)
                else:
                    pack_datas['picking_id'] = self.picking_id.id
                    operation_obj.create(pack_datas)
        return True
