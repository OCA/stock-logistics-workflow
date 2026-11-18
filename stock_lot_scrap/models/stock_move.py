# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_scrap(self):
        for lot in self.lot_ids:
            lot.message_post(
                body=Markup(
                    self.env._(
                        "Lot was scrapped by <b>%(name)s</b>.", name=self.env.user.name
                    )
                )
            )
        return super()._action_scrap()
