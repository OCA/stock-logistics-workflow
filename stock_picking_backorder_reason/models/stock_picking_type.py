# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    backorder_reason = fields.Boolean(
        help="Check this if you want people selecting a backorder reason when applicable."
        "This will trigger a backorder strategy rule defined on that reason."
    )
    backorder_reason_sale = fields.Boolean(
        compute="_compute_backorder_reason_sale",
        readonly=False,
        store=True,
        help="Check this in order to consider pickings in this type as Sale ones for "
        "backorder reason cancellation.",
    )
    backorder_reason_purchase = fields.Boolean(
        compute="_compute_backorder_reason_purchase",
        readonly=False,
        store=True,
        help="Check this in order to consider pickings in this type as "
        "Purchase ones for backorder reason cancellation.",
    )

    @api.depends("backorder_reason")
    def _compute_backorder_reason_sale(self):
        activated_types = self.filtered("backorder_reason_sale")
        to_deactivate = activated_types.filtered(lambda t: not t.backorder_reason)
        to_deactivate.update({"backorder_reason_sale": False})

    @api.depends("backorder_reason")
    def _compute_backorder_reason_purchase(self):
        activated_types = self.filtered("backorder_reason_purchase")
        to_deactivate = activated_types.filtered(lambda t: not t.backorder_reason)
        to_deactivate.update({"backorder_reason_purchase": False})

    @api.constrains(
        "backorder_reason", "backorder_reason_sale", "backorder_reason_purchase"
    )
    def _check_backorder_reason(self):
        for picking_type in self.filtered("backorder_reason"):
            if (
                not picking_type.backorder_reason_sale
                and not picking_type.backorder_reason_purchase
            ):
                raise ValidationError(
                    _(
                        "If you enable the backorder reason feature, you should "
                        "choose if this is for sale or purchase."
                    )
                )
