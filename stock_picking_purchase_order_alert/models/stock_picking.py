import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    has_quantity_alert = fields.Boolean(
        string="Quantity Alert",
        compute="_compute_has_quantity_alert",
        store=False,
        help="Indicates if any move line exceeds ordered "
        "quantity by more than threshold",
    )
    quantity_alert_message = fields.Html(
        string="Quantity Alert Message",
        compute="_compute_has_quantity_alert",
        store=False,
    )

    @api.depends(
        "move_ids_without_package",
        "move_ids_without_package.quantity_done",
        "move_ids_without_package.purchase_line_id",
    )
    def _compute_has_quantity_alert(self):
        """Compute if there are any moves with quantities that exceed PO
        quantities by more than configured threshold percentage.
        """

        for picking in self:
            picking.has_quantity_alert = False
            picking.quantity_alert_message = False

            if not (
                picking.picking_type_id.display_quantity_alert_percentage
                and picking.picking_type_id.code == "incoming"
                and picking.purchase_id
            ):
                continue

            alert_lines = self._get_quantity_alert_lines(picking)
            if not alert_lines:
                continue

            picking.has_quantity_alert = True
            picking.quantity_alert_message = self._format_quantity_alert_message(
                picking.picking_type_id.quantity_alert_percentage,
                alert_lines,
            )

    @api.model
    def _get_group_names(self, groups_ids):
        groups = self.env["ir.model.data"].search(
            [("model", "=", "res.groups"), ("res_id", "in", groups_ids)]
        )
        groups_names = [f"{group.module}.{group.name}" for group in groups]
        return ",".join(groups_names)

    def _get_quantity_alert_lines(self, picking):
        """Get lines that exceed the configured threshold percentage."""
        alert_lines = []
        alert_pct = picking.picking_type_id.quantity_alert_percentage
        threshold_factor = 1 + (alert_pct / 100.0)

        moves_with_qty = picking.move_ids_without_package.filtered(
            lambda m: m.purchase_line_id and m.quantity_done > 0
        )

        for move in moves_with_qty:
            po_line = move.purchase_line_id
            po_qty = po_line.product_qty

            if not po_qty > 0:
                continue

            received_qty = move.product_uom._compute_quantity(
                move.quantity_done, po_line.product_uom
            )

            if received_qty <= po_qty * threshold_factor:
                continue

            excess_percent = (received_qty / po_qty - 1) * 100
            alert_lines.append(
                {
                    "product": move.product_id.display_name,
                    "ordered": po_qty,
                    "ordered_uom": po_line.product_uom.name,
                    "received": received_qty,
                    "received_uom": po_line.product_uom.name,
                    "percent": excess_percent,
                    "threshold": picking.picking_type_id.quantity_alert_percentage,
                }
            )

        return alert_lines

    def _format_quantity_alert_message(self, alert_percentage, alert_lines):
        """Format the HTML message for quantity alerts."""
        message = (
            "<div class='alert alert-warning'>"
            "<strong>Warning!</strong> Material with quantity "
            "exceeding ordered amount detected (threshold: "
            f"{alert_percentage}%): <br/>"
            "<ul>"
        )

        msg_line_template = (
            "<li><strong>{product}</strong>: "
            "Ordered: {ordered} {ordered_uom}, "
            "To receive: {received} {received_uom} "
            "(excess of {percent:.2f}%)</li>"
        )

        message += "".join(msg_line_template.format(**line) for line in alert_lines)
        message += "</ul></div>"

        return message

    def button_validate(self):
        """Override button_validate to prevent validation
        when quantity alerts exist"""
        for picking in self:
            groups_ids = picking.picking_type_id.groups_ids
            if groups_ids and not (
                self.env.user.user_has_groups(self._get_group_names(groups_ids.ids))
            ):
                group_names = [f"- {group.display_name}" for group in groups_ids]
                error_msg = _(
                    "In order to validate this picking you need to belong to any"
                    "of this groups:\n%s"
                ) % "\n".join(group_names)
                raise UserError(error_msg)

            if picking.has_quantity_alert and "bypass_alert" not in self.env.context:
                return {
                    "type": "ir.actions.act_window",
                    "name": _("Quantity Alert"),
                    "res_model": "stock.picking.alert.wizard",
                    "view_mode": "form",
                    "target": "new",
                    "context": {
                        "default_picking_id": picking.id,
                    },
                }

        return super().button_validate()
