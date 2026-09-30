# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    # TODO: This module should be split with the 'partner' backorder strategy
    # The reason should be added on top of that
    backorder_reason = fields.Boolean(
        help="Check this if you want people selecting a backorder reason when applicable."
        "This will trigger a backorder strategy rule defined on that reason."
    )
    backorder_reason_sale = fields.Boolean(
        help="Check this in order to consider pickings in this type as Sale ones for "
        "backorder reason cancellation.",
    )
    backorder_reason_purchase = fields.Boolean(
        help="Check this in order to consider pickings in this type as "
        "Purchase ones for backorder reason cancellation.",
    )
    backorder_reason_transparent_cancel = fields.Boolean(
        help="If this is checked and if the partner strategy is 'Cancel', "
        "nothing will be shown to the user and the backorder will be cancelled."
    )

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
