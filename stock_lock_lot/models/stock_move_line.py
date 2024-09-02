# Copyright 2016 AvanzOsc (http://www.avanzosc.es)
# Copyright 2024 Adriana Saiz <adriana.saiz@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, exceptions, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        for ml in self:
            if ml.lot_id.locked and not ml.location_dest_id.allow_locked:
                raise exceptions.ValidationError(
                    _(
                        "The following lots/serial number is blocked and "
                        "cannot be moved:\n%s"
                    )
                    % ml.lot_id.name
                )
        return super()._action_done()
