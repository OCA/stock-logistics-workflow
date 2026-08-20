# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockDateDoneMixin(models.AbstractModel):
    _name = "stock.date.done.mixin"
    _description = "Stock Date Done Mixin"

    origin_date_done = fields.Datetime(
        string="Original Effective Date",
        readonly=True,
        copy=False,
        help="The actual processing timestamp captured the first time the "
        "record was done. Unlike the effective date it is never overwritten, "
        "so it stays an audit reference even after the effective date is "
        "edited.",
    )
    is_date_done_editable = fields.Boolean(
        compute="_compute_is_date_done_editable",
        help="Technical: whether the current user may edit the effective date.",
    )
    date_done_edited = fields.Boolean(
        compute="_compute_date_done_edited",
        help="Technical: the effective date differs from the original "
        "processing timestamp (i.e. it was back-dated).",
    )

    def _date_done_editable_by_group(self):
        return self.env.user.has_group("stock_date_done.group_date_done_editable")

    def _compute_is_date_done_editable(self):
        can_edit = self._date_done_editable_by_group()
        for rec in self:
            rec.is_date_done_editable = rec.state != "done" or can_edit

    @api.depends("origin_date_done")
    def _compute_date_done_edited(self):
        for rec in self:
            rec.date_done_edited = bool(rec.origin_date_done) and (
                rec.origin_date_done != rec.date_done
            )

    def _set_date_done_origin(self, preset):
        for rec in self:
            if not rec.origin_date_done:
                rec.origin_date_done = rec.date_done
            target = preset.get(rec.id)
            if target and rec.date_done != target:
                rec.date_done = target
