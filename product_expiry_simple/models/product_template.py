# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    use_expiry_date = fields.Boolean(
        compute="_compute_use_expiry_date", store=True, readonly=False, precompute=True
    )

    @api.depends("tracking")
    def _compute_use_expiry_date(self):
        self.filtered(lambda pt: pt.tracking == "none").use_expiry_date = False

    @api.constrains("tracking", "use_expiry_date")
    def _check_use_expiry_date(self):
        for ptemplate in self:
            if ptemplate.use_expiry_date and ptemplate.tracking not in (
                "lot",
                "serial",
            ):
                raise ValidationError(
                    _(
                        "You cannot set 'Use Expiry Date' on product '%s' because "
                        "it is not tracked by lot nor by serial number."
                    )
                    % ptemplate.display_name
                )
