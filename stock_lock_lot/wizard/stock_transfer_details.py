# -*- coding: utf-8 -*-
# © 2016 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    allow_locked = fields.Boolean(string="Allow Locked",
                                  related="destinationloc_id.allow_locked")
