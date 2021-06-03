# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from odoo import models, fields, api
from odoo import http


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()

        deliveryslip_folder =\
            self.picking_type_id.warehouse_id.deliveryslip_folder
        if deliveryslip_folder and self.picking_type_id.code == 'outgoing':
            report_obj = self.env["ir.actions.report"]
            report = report_obj._get_report_from_name(
                'stock.report_deliveryslip'
            )
            pdf_content, format = report.render_qweb_pdf(self.ids)

            filename = self.name.replace('/', '-') + '.' + format
            full_path = os.path.join(deliveryslip_folder, filename)
            with open(full_path, 'wb') as file_handle:
                file_handle.write(pdf_content)
        return res
