# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
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

from openerp import models, api

report_name = 'stock_picking_pallet.report_picking_pallet'


class PickingPackagePreparationReport(models.AbstractModel):
    _name = 'report.%s' % report_name

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(report_name)
        preparation_model = self.env['stock.picking.package.preparation']
        preparations = preparation_model.browse(self.ids)

        docargs = {
            'doc_ids': preparations.ids,
            'doc_model': report.model,
            'docs': preparations,
        }
        return report_obj.render(report_name, docargs)
