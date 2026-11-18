# Copyright (C) 2023-Today:
# Dinamiche Aziendali Srl (<http://www.dinamicheaziendali.it/>)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Giuseppe Borruso <gborruso@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from xlsxwriter.utility import xl_rowcol_to_cell

from odoo import _, models


class XlsxStockClosePeriod(models.AbstractModel):
    _name = "report.stock_close_period.report_xlsx_stock_close_print"
    _inherit = "report.report_xlsx.abstract"
    _description = "Report Stock Close XLSX"

    def generate_xlsx_report(self, workbook, data, lines):
        if data.get("ids"):
            ids = data["ids"]
            lines = self.env["stock.close.period.line"].browse(ids)

        sheet = workbook.add_worksheet(_("Stock Close Period"))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.fit_to_pages(1, 0)
        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 50)
        sheet.set_column(2, 2, 50)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 15)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 8, 10)
        sheet.set_column(9, 9, 15)
        sheet.set_column(10, 10, 20)

        title_style = workbook.add_format(
            {"bold": False, "bg_color": "#C0C0C0", "bottom": 1}
        )
        currency_format = workbook.add_format({"num_format": "€ #,##0.00"})
        currency_format_title = workbook.add_format(
            {
                "num_format": "€ #,##0.00",
                "bold": False,
                "bg_color": "#C0C0C0",
                "bottom": 1,
            }
        )

        # header
        sheet_title = [
            _("Product"),
            _("Name"),
            _("Category"),
            _("Location"),
            _("Lot/Serial Number"),
            _("Owner"),
            _("Evaluation"),
            _("Quantity"),
            _("Uom"),
            _("Unit Cost"),
            _("Total Cost"),
        ]
        i = 0
        sheet.write_row(i, 0, sheet_title, title_style)
        sheet.freeze_panes(1, 0)
        i = 1

        # rows
        for row in lines:
            total_price = row.product_qty * row.price_unit
            sheet.write(i, 0, row.product_code or "")
            sheet.write(i, 1, row.product_id.with_context(lang="it_IT").name or "")
            sheet.write(i, 2, row.categ_name or "")
            sheet.write(i, 3, row.location_id.display_name or "")
            sheet.write(i, 4, row.lot_id.name or "")
            sheet.write(i, 5, row.owner_id.name or "")
            sheet.write(i, 6, row.evaluation_method or "")
            sheet.write(i, 7, round(row.product_qty))
            sheet.write(i, 8, row.product_uom_id.name)
            sheet.write(i, 9, row.price_unit, currency_format)
            sheet.write(i, 10, total_price, currency_format)
            i += 1
        sheet.write(i, 9, _("Total"), title_style)
        sheet.write_formula(
            i,
            10,
            "=SUM(%s:%s)"
            % (
                xl_rowcol_to_cell(1, 10),
                xl_rowcol_to_cell(i - 1, 10),
            ),
            currency_format_title,
            "",
        )
