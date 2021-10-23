# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "tier.validation"]
    _state_from = ["draft", "waiting", "confirmed", "assigned"]
    _state_to = ["done", "approved"]

    _tier_validation_manual_config = False

    def button_validate(self):
        for rec in self:
            if rec.need_validation:
                # try to validate operation
                reviews = rec.request_validation()
                rec._validate_tier(reviews)
                if not self._calc_reviews_validated(reviews):
                    raise ValidationError(
                        _(
                            "This action needs to be validated for at least "
                            "one record. \nPlease request a validation."
                        )
                    )
            if rec.review_ids and not rec.validated:
                raise ValidationError(
                    _("A validation process is still open for at least one record.")
                )
        return super().button_validate()
