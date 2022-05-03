# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError

import xlrd


class StockPickingImportSerialNumber(models.TransientModel):
    _name = "stock.picking.import.serial.number.wiz"
    _description = "Import S/N wizard"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if (
            self.env.context.get("active_ids")
            and self.env.context.get("active_model") == "stock.picking"
        ):
            pickings = self.env["stock.picking"].browse(
                self.env.context.get("active_ids")
            )
            if pickings.exists():
                res.update({"picking_ids": [(6, 0, pickings.ids)]})
        return res

    search_product_by_field = fields.Selection(
        [("default_code", "Reference"), ("barcode", "Barcode")],
        string="Search product by field",
        default="default_code",
    )
    product_column_index = fields.Integer(string="Column index for product", default=0)
    serial_column_index = fields.Integer(string="Column index for S/N", default="1")
    picking_ids = fields.Many2many("stock.picking")
    data_file = fields.Binary(string="File to import")
    filename = fields.Char(string="Filename")
    overwrite_serial = fields.Boolean()

    def action_import(self):
        if self.picking_ids.filtered(lambda p: p.picking_type_id.code != "incoming"):
            raise UserError(_("You only can import S/N for incoming moves"))
        if self.picking_ids.filtered(lambda p: not p.picking_type_id.use_create_lots):
            raise UserError(
                _(
                    "You only can import S/N for picking operations with"
                    " creation lots checked"
                )
            )
        if not self.data_file:
            raise UserError(_("You must upload file to import records"))
        xl_workbook = False
        xl_sheet = False
        if self.filename.split(".")[1] in ["xls", "xlsx"]:
            xl_workbook = xlrd.open_workbook(
                file_contents=base64.b64decode(self.data_file)
            )
            xl_sheet = xl_workbook.sheet_by_index(0)
            move_lines = self.picking_ids.mapped("move_line_ids").filtered(
                lambda ln: ln.product_id.tracking == "serial"
                and ln.picking_id.picking_type_id.use_create_lots
            )
            self._import_serial_number(xl_sheet, move_lines)
        self.data_file = False

    def _import_serial_number(self, xl_sheet, stock_move_lines):
        product_file_list = []
        serial_list = []
        for row_idx in range(1, xl_sheet.nrows):
            product = str(xl_sheet.cell(row_idx, self.product_column_index).value)
            serial = str(xl_sheet.cell(row_idx, self.serial_column_index).value)
            product_file_list.append(product)
            serial_list.append((product, serial))

        products = self.env["product.product"].search(
            [(self.search_product_by_field, "in", product_file_list)]
        )
        for item in serial_list:
            product = products.filtered(
                lambda p: p[self.search_product_by_field]
                == item[self.product_column_index]
            )
            smls = stock_move_lines.filtered(lambda ln: ln.product_id == product)
            for sml in smls:
                if not sml.lot_name or self.overwrite_serial:
                    sml.lot_name = item[self.serial_column_index]
                    # Only assign one serial
                    break
