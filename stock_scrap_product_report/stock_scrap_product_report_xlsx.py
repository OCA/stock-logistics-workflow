# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import models, _

_logger = logging.getLogger(__name__)


class ReportStockScrapProductReportXlsx(models.TransientModel):
    _name = 'report.report_stock_scrap_product_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def _get_ws_params(self, wb, data, objects):

        stock_scrap_product_template = {
            '1_number': {
                'header': {
                    'value': '#',
                },
                'data': {
                    'value': self._render('n'),
                },
                'width': 12,
            },
            '2_reference': {
                'header': {
                    'value': _('Reference'),
                },
                'data': {
                    'value': self._render('reference'),
                },
                'width': 15,
            },
            '3_name': {
                'header': {
                    'value': _('Name'),
                },
                'data': {
                    'value': self._render('name'),
                },
                'width': 36,
            },
            '4_categ_name': {
                'header': {
                    'value': _('Internal Category'),
                },
                'data': {
                    'value': self._render('categ_name'),
                },
                'width': 36,
            },
            '5_barcode': {
                'header': {
                    'value': _('Barcode'),
                },
                'data': {
                    'value': self._render('barcode'),
                },
                'width': 15,
            },
            '6_qty_at_date': {
                'header': {
                    'value': _('Quantity'),
                },
                'data': {
                    'value': self._render('qty_at_date'),
                    'format': self.format_tcell_amount_conditional_right,
                },
                'width': 18,
            },
            '7_date': {
                'header': {
                    'value': _('Date'),
                },
                'data': {
                    'value': self._render('date'),
                    'format': self.format_tcell_date_left,
                },
                'width': 15,
            },
            '80_standard_price': {
                'header': {
                    'value': _('Cost'),
                },
                'data': {
                    'value': self._render('standard_price'),
                    'format': self.format_tcell_amount_conditional_right,
                },
                'width': 18,
            },
            '81_stock_value': {
                'header': {
                    'value': _('Value'),
                },
                'data': {
                    'value': self._render('stock_value'),
                    'format': self.format_tcell_amount_conditional_right,
                },
                'width': 18,
            },
            '90_origin': {
                'header': {
                    'value': _('Origin'),
                },
                'data': {
                    'value': self._render('origin'),
                },
                'width': 18,
            },
        }

        ws_params = {
            'ws_name': _('Scrap Report'),
            'generate_ws_method': '_scrap_product_report',
            'title': 'Scrap Report',
            'wanted_list': [k for k in sorted(
                stock_scrap_product_template.keys())],
            'col_specs': stock_scrap_product_template,
        }
        return [ws_params]

    def _scrap_product_report(self, wb, ws, ws_params, data, objects):

        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(self.xls_headers['standard'])
        ws.set_footer(self.xls_footers['standard'])

        self._set_column_width(ws, ws_params)

        row_pos = 0
        row_pos = self._write_ws_title(ws, row_pos, ws_params, True)

        for o in objects:
            ws.write_row(
                row_pos, 0, [_('Start Date'), _('End Date'), _('Partner'), _('Tax ID')],
                self.format_theader_blue_center)
            ws.write_row(
                row_pos+1, 0, [o.start_date or '', o.end_date or ''],
                self.format_tcell_date_center)
            ws.write_row(
                row_pos+1, 2,
                [o.company_id.name or '', o.company_id.vat or ''],
                self.format_tcell_center)

            row_pos += 3
            row_pos = self._write_line(
                ws, row_pos, ws_params, col_specs_section='header',
                default_format=self.format_theader_blue_center)
            ws.freeze_panes(row_pos, 0)

            total = 0.00
            for line in o.results:
                row_pos = self._write_line(
                    ws, row_pos, ws_params, col_specs_section='data',
                    render_space={
                        'n': row_pos-5,
                        'name': line.name or '',
                        'reference': line.reference or '',
                        'barcode': line.barcode or '',
                        'qty_at_date': line.qty_at_date or 0.000,
                        'standard_price': line.standard_price or 0.00,
                        'stock_value': line.stock_value or 0.00,
                        'categ_name': line.categ_name,
                        'date': line.date,
                        'origin': line.origin or '',
                    },
                    default_format=self.format_tcell_left)
                total += line.stock_value

            ws.write(row_pos, 8, total, self.format_theader_blue_amount_right)
