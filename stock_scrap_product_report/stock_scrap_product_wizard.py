##############################################################################
#
#    Copyright since 2009 Trobz (<https://trobz.com/>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models


class StockScrapProductWizardView(models.TransientModel):
    _name = 'stock.scrap.product.wizard.view'
    _description = 'Wizard for Scrap Report View'

    name = fields.Char()
    reference = fields.Char()
    barcode = fields.Char()
    qty_at_date = fields.Float()
    uom_id = fields.Many2one(
        comodel_name='uom.uom',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
    )
    cost_currency_id = fields.Many2one(
        comodel_name='res.currency',
    )
    standard_price = fields.Float()
    stock_value = fields.Float()
    cost_method = fields.Char()
    categ_name = fields.Char()
    date = fields.Datetime()

class StockScrapProductWizard(models.TransientModel):
    _name = 'stock.scrap.product.wizard'
    _description = "Wizard for Scrap Report"

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id.id
    )
    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True)

    # Data fields, used to browse report data
    results = fields.Many2many(
        comodel_name='stock.scrap.product.wizard.view',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        ReportLine = self.env['stock.scrap.product.wizard.view']
        move_lines = self.get_scrap_move_lines(
            self.start_date, self.end_date)
        for move_line in move_lines:
            product = move_line.product_id.with_context(
                dict(to_date=move_line.date, company_owned=True,
                create=False, edit=False))
            standard_price = product.get_history_price(
                self.env.user.company_id.id,
                date=move_line.date)
            line = self.parse_line(
                product, standard_price, move_line.qty_done, move_line.date)
            self.results += ReportLine.new(line)

    @api.model
    def parse_line(self, product, standard_price, qty, date):
        line = {
            'name': product.name,
            'reference': product.default_code,
            'barcode': product.barcode,
            'qty_at_date': qty,
            'uom_id': product.uom_id,
            'currency_id': product.currency_id,
            'cost_currency_id': product.cost_currency_id,
            'standard_price': standard_price,
            'stock_value': qty * standard_price,
            'cost_method': product.cost_method,
            'categ_name': product.categ_id.name,
            'date': date,
        }
        return line

    @api.model
    def get_scrap_locations(self):
        locations = self.env['stock.location'].search(
            [('scrap_location', '=', True)]
        )
        return locations

    @api.model
    def get_scrap_move_lines(self, start_date, end_date):
        locations = self.get_scrap_locations()
        args = [
            ('location_dest_id', 'in', locations.mapped('id')),
            ('state', '=', 'done')
        ]
        if start_date:
            args.append(('date', '>=', start_date))
        if end_date:
            args.append(('date', '<=', end_date))

        move_lines = self.env['stock.move.line'].search(args)
        return move_lines

    def button_export_xlsx(self):
        self.ensure_one()
        action = self.env.ref(
            'stock_scrap_product_report.'
            'action_stock_scrap_report_xlsx')
        return action.report_action(self, config=False)
