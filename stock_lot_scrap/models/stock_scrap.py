# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    def action_validate(self):
        self.ensure_one()
        self.lot_id.message_post(
            body=_("Lot was scrapped by <b>%s</b>.") % self.env.user.name
        )
        return super().action_validate()
