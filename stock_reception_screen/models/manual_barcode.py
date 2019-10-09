# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockPickingManualBarcode(models.TransientModel):
    _name = "stock.picking.manual.barcode"
    _description = "Action to input a barcode"

    barcode = fields.Char(string="Barcode")

    def button_save(self):
        self.ensure_one()
        record_id = self.env.context.get('active_id')
        record = self.env["stock.picking"].browse(record_id).exists()
        if not record:
            return
        if self.barcode:
            record.on_barcode_scanned(self.barcode)
