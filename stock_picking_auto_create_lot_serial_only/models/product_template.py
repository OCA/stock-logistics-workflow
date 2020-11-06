# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):

    _inherit = "product.template"

    @api.constrains("auto_create_lot", "tracking")
    def _check_auto_create_lot(self):
        for rec in self:
            if rec.auto_create_lot and rec.tracking != "serial":
                raise ValidationError(
                    _(
                        "The automatic serial generation is only available"
                        "for products with tracking per serial."
                    )
                )
