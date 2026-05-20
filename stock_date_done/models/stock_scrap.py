# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StockScrap(models.Model):
    _name = "stock.scrap"
    _inherit = ["stock.scrap", "stock.date.done.mixin"]

    # Editable so that an effective date can be set before or after validation.
    date_done = fields.Datetime(readonly=False)

    def _compute_is_date_done_editable(self):
        res = super()._compute_is_date_done_editable()
        for scrap in self:
            if scrap.is_date_done_editable and scrap.state == "done":
                scrap.is_date_done_editable = not scrap._is_date_in_lock_period()
        return res

    @api.constrains("date_done")
    def _check_backdate_allowed(self):
        # Same escape hatch as core's stock.picking check: Odoo's upgrade test
        # suite sets it after moving lock dates forward (odoo/odoo#236926).
        if (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("stock_account.skip_lock_date_check")
        ):
            return
        for scrap in self:
            if scrap._is_date_in_lock_period():
                raise ValidationError(
                    self.env._(
                        "You cannot modify the effective date of scrap %s because "
                        "it falls within a locked fiscal period.",
                        scrap.display_name,
                    )
                )

    def write(self, vals):
        res = super().write(vals)
        if vals.get("date_done"):
            for scrap in self.filtered(lambda s: s.state == "done"):
                done_moves = scrap.move_ids.filtered(lambda m: m.state == "done")
                if done_moves:
                    done_moves.date = vals["date_done"]
        return res

    def do_scrap(self):
        preset = {scrap.id: scrap.date_done for scrap in self}
        res = super().do_scrap()
        self._set_date_done_origin(preset)
        return res

    def _is_date_in_lock_period(self):
        self.ensure_one()
        if not self.date_done:
            return False
        return bool(
            self.company_id._get_lock_date_violations(
                fields.Date.context_today(self, self.date_done),
                fiscalyear=True,
                sale=False,
                purchase=False,
                tax=False,
                hard=True,
            )
        )
