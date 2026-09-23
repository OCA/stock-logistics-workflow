# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockScrap(models.Model):
    _name = "stock.scrap"
    _inherit = ["stock.scrap", "stock.date.done.mixin"]

    # Core defines ``date_done`` as readonly and only stamps it with now() at
    # ``do_scrap`` time. Make it user-editable so an effective scrap date can be
    # set up front. No default on purpose: left empty, core stamps the real
    # processing time on do_scrap (and origin == date_done, so it reads as
    # "not edited"); a default of now() would be treated as a pre-set value and
    # spuriously flagged as edited. Mirrors pickings, which have no default.
    date_done = fields.Datetime(readonly=False)

    def do_scrap(self):
        preset = {scrap.id: scrap.date_done for scrap in self}
        res = super().do_scrap()
        self._set_date_done_origin(preset)
        return res

    def write(self, vals):
        res = super().write(vals)
        if vals.get("date_done"):
            for scrap in self.filtered(lambda s: s.state == "done"):
                done_moves = scrap.move_ids.filtered(lambda m: m.state == "done")
                if done_moves:
                    done_moves.date = vals["date_done"]
        return res
