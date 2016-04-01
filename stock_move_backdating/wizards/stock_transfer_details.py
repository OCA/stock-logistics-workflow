# -*- coding: utf-8 -*-
# © 2016 Agile Business Group (<http://www.agilebg.com>)
# © 2015 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


def check_date(date):
    now = fields.Datetime.now()
    if date > now:
        raise UserError(
            _("You can not process an actual "
              "movement date in the future."))


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    date_backdating = fields.Datetime(string='Actual Movement Date')

    @api.onchange('date_backdating')
    def onchange_date_backdating(self):
        check_date(self.date_backdating)
        for item in self.item_ids:
            item.date = self.date_backdating
        for packop in self.packop_ids:
            packop.date = self.date_backdating

    @api.model
    def default_get(self, fields_list):
        res = super(StockTransferDetails, self).default_get(fields_list)
        now = fields.Datetime.now()
        res['date_backdating'] = now
        for item in res['item_ids']:
            item['date'] = now
        for packop in res['packop_ids']:
            packop['date'] = now
        return res


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    @api.onchange('date')
    def onchange_date(self):
        check_date(self.date)
