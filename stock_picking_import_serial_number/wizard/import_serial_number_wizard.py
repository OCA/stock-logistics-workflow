# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

import xlrd

from odoo import _, api, fields, models
from odoo.exceptions import UserError


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

    picking_ids = fields.Many2many("stock.picking")
    data_file = fields.Binary(string="File to import")
    filename = fields.Char(string="Filename")
    overwrite_serial = fields.Boolean()
    # Fields filled by settings. This names are special
    sn_search_product_by_field = fields.Selection(
        [("default_code", "Reference"), ("barcode", "Barcode")],
        string="Search product by field",
        default="default_code",
    )
    sn_product_column_index = fields.Integer(
        string="Column index for product", default=0
    )
    sn_serial_column_index = fields.Integer(string="Column index for S/N", default="1")

    def action_import(self):
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
            for picking in self.picking_ids:
                move_lines = picking.mapped("move_line_ids").filtered(
                    lambda ln: ln.product_id.tracking == "serial"
                    and ln.picking_id.picking_type_id.use_create_lots
                )
                self._import_serial_number(xl_sheet, move_lines, picking)
        self.data_file = False

    def _import_serial_number(self, xl_sheet, stock_move_lines, picking):
        product_file_set = set()
        serial_list = []
        for row_idx in range(1, xl_sheet.nrows):
            product = str(xl_sheet.cell(row_idx, self.sn_product_column_index).value)
            serial = str(xl_sheet.cell(row_idx, self.sn_serial_column_index).value)
            product_file_set.add(product)
            serial_list.append((product, serial))

        products = self.env["product.product"].search(
            [(self.sn_search_product_by_field, "in", list(product_file_set))]
        )
        for item in serial_list:
            product = products.filtered(
                lambda p: p[self.sn_search_product_by_field] == item[0]
            )
            if picking.picking_type_id.show_reserved:
                smls = stock_move_lines.filtered(lambda ln: ln.product_id == product)
                for sml in smls:
                    if not sml.lot_name or self.overwrite_serial:
                        sml.lot_name = item[1]
                        sml.qty_done = 1.0
                        # Only assign one serial
                        break
            # TODO: Check if product is present on initial demand??
            # elif product and picking.move_lines.filtered(lambda ln: ln.product_id == product)
            elif product:
                self.env["stock.move.line"].create(
                    {
                        "picking_id": picking.id,
                        "location_id": picking.location_id.id,
                        "location_dest_id": picking.location_dest_id.id,
                        "product_id": product.id,
                        "product_uom_id": product.uom_id.id,
                        "lot_name": item[1],
                        "product_uom_qty": 0.0,
                        "qty_done": 1.0,
                    }
                )
