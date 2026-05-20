# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "stock.date.done.mixin"]

    @api.depends("is_date_editable", "state")
    def _compute_is_date_done_editable(self):
        can_edit = self._date_done_editable_by_group()
        for picking in self:
            if picking.state in ("done", "cancel"):
                picking.is_date_done_editable = picking.is_date_editable and can_edit
            else:
                picking.is_date_done_editable = True

    def _action_done(self):
        preset = {picking.id: picking.date_done for picking in self}
        res = super()._action_done()
        self._set_date_done_origin(preset)
        return res
