# Copyright (C) 2023-Today:
# Dinamiche Aziendali Srl (<http://www.dinamicheaziendali.it/>)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Giuseppe Borruso <gborruso@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import csv
import io
import logging
from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class StockCloseImportWizard(models.TransientModel):
    _name = "stock.close.import.wizard"
    _description = "Stock Close Import Wizard"

    file = fields.Binary()
    close_id = fields.Many2one("stock.close.period", string="Stock Close Period")

    def load_products(self, lines):
        products = {}
        for row in lines:
            default_code = row["CODE"]
            product_obj = self.env["product.product"].search(
                [("default_code", "=", default_code)], limit=1
            )
            if not product_obj:
                raise UserError(_("Product %s not found") % default_code)
            products[default_code] = product_obj[0]
        return products

    def import_csv(self):
        # set done close_id
        self.close_id.work_start = datetime.now()

        try:
            file_to_import = base64.b64decode(self.file)
            data_file = io.StringIO(file_to_import.decode("utf-8"))
            data_file.seek(0)
            reader = csv.DictReader(data_file, delimiter=";")
            lines = []

            for row in reader:
                lines.append(
                    {
                        "CODE": str(row["CODE"]),
                        "COST": str(row["COST"]).replace(",", "."),
                        "QTY": str(row["QTY"]).replace(",", "."),
                    }
                )
            products = self.load_products(lines)
            total = 0.0
            dp_qty = 4
            dp_price = 5
            for row in lines:
                product_id = products[row["CODE"]].id
                unit_cost = round(float(row["COST"]), dp_price)
                qty = round(float(row["QTY"]), dp_qty)
                total += unit_cost * qty
                self.env["stock.close.period.line"].with_context(
                    tracking_disable=True
                ).create(
                    {
                        "close_id": self.close_id.id,
                        "product_id": product_id,
                        "price_unit": unit_cost,
                        "product_qty": qty,
                        "product_uom_id": products[
                            row["CODE"]
                        ].product_tmpl_id.uom_id.id,
                        "evaluation_method": "",
                    }
                )

            # set done close_id
            self.close_id.amount = total
            self.close_id.work_end = datetime.now()
            self.close_id.state = "done"

        except Exception as e:
            raise UserError(e) from e
