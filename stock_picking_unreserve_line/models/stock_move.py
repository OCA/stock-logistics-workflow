# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def do_unreserve(self):
        self.ensure_one()

        self._do_unreserve()
        if self.picking_id:
            self.picking_id.package_level_ids.filtered(
                lambda p: not p.move_ids).unlink()
        return True
