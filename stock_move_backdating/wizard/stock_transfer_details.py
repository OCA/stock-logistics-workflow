# -*- coding: utf-8 -*-
# ©2015 Agile Business Group (<http://www.agilebg.com>)
# ©2015 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from datetime import datetime


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    _defaults = {
        'date': fields.Datetime.now,
    }

    @api.one
    @api.constrains('date')
    def check_date(self):
        if self.date:
            now = datetime.utcnow()
            dt = fields.Datetime.from_string(self.date)
            if dt > now:
                raise UserError(
                    _(
                        "You can not process an actual"
                        " movement date in the future."
                    )
                )
