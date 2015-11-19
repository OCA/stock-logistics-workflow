# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Agile Business Group (<http://www.agilebg.com>)
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

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


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
            if  dt > now:
                raise Warning(
                    _("You can not process an actual movement date in the future.")
                )
