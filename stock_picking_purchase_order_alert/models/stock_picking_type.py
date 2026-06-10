from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    display_quantity_alert_percentage = fields.Boolean(
        string="Display Quantity Alert",
        default=False,
    )
    quantity_alert_percentage = fields.Float(
        string="Quantity Alert Percentage",
        default=30.0,
        help="Percentage threshold for quantity alert in receipts. "
        "Default is 30%. Set to 0 to disable alerts.",
    )

    groups_ids = fields.Many2many(
        comodel_name="res.groups",
        help="The user must be a member of at least one specified group. "
        "If no groups are specified, the alert can be bypassed by any user.",
    )

    @api.constrains("quantity_alert_percentage")
    def _check_quantity_alert_percentage(self):
        if self.quantity_alert_percentage <= 0:
            raise UserError(_("Quantity alert percentage must be greater than zero."))
