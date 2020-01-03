# Copyright 2019 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def _get_moves(self):
        return self.filtered(
            lambda x: x.state == 'done' and
            not x.scrapped and (
                x.location_id.usage == 'supplier' or
                (x.location_dest_id.usage == 'customer' and
                 x.to_refund)
            ))
