# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re

from odoo import _, fields, models


class StockPickingNotificationTemplate(models.Model):
    _name = "stock.picking.notification.template"
    _description = "Picking Notification Template"
    _order = "sequence, id"
    _rec_name = "picking_type_id"

    sequence = fields.Integer(
        default=10,
        string="Priority",
    )
    active = fields.Boolean(
        default=True,
    )
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Operation Type",
        required=True,
        help="Operation types for which the notification will be triggered",
    )
    user_ids = fields.Many2many(
        string="Notified Users",
        comodel_name="res.users",
        relation="picking_notify_template_user_rel",
        column1="picking_notify_template_id",
        column2="user_id",
        required=True,
    )
    source_document_regex = fields.Char(
        string="Source Document Pattern",
        help="Notification will be sent if source document name matches "
        "the specified regex pattern. Leave blank to match any source",
    )
    allow_notify_draft = fields.Boolean(
        string="Allow Notify DRAFT",
        default=False,
    )
    allow_notify_waiting = fields.Boolean(
        string="Allow Notify WAITING ANOTHER OPERATION",
        default=False,
    )
    allow_notify_confirmed = fields.Boolean(
        string="Allow notify WAITING",
        default=True,
    )
    allow_notify_assigned = fields.Boolean(
        string="Allow notify READY",
        default=True,
    )
    allow_notify_done = fields.Boolean(
        string="Allow notify DONE",
        default=False,
    )
    allow_notify_cancel = fields.Boolean(
        string="Allow notify CANCEL",
        default=False,
    )
    message = fields.Text(
        string="Custom Message",
        help="Custom message to be used instead of the default one. "
        "Leave blank to use the default message",
    )
    notification_sound_file = fields.Binary(
        string="Notification Sound",
        attachment=True,
        help="Select the sound file that will be used for notifications. This setting "
        "allows you to customize the notification sound played when certain actions "
        "occur, such as when a stock picking status is updated.",
    )
    filename = fields.Char()

    def _get_matching_template(self, picking):
        """
        Return the first matching notification template for the given picking.
        """
        templates = self.search(
            [
                ("picking_type_id", "=", picking.picking_type_id.id),
                (f"allow_notify_{picking.state}", "=", True),
            ],
            order="sequence ASC",
        )
        for template in templates:
            if template._matches_picking(picking):
                return template
        return None

    def _matches_picking(self, picking):
        """
        Check if the picking matches this notification template.
        """
        if self.source_document_regex and not re.match(
            self.source_document_regex, picking.origin or ""
        ):
            return False

        return True

    def _get_sound_path(self):
        """
        Return sound notification path if sound is specified
        """
        self.ensure_one()
        if self.notification_sound_file:
            attachment = self.env["ir.attachment"].search(
                [
                    ("res_model", "=", self._name),
                    ("res_field", "=", "notification_sound_file"),
                    ("res_id", "=", self.id),
                ]
            )
            attachment.generate_access_token()
            return (
                f"/web/content/{attachment.id}?access_token={attachment.access_token}"
            )

    def _notify_picking_users(self, picking):
        """
        Send notifications to the users about the picking.
        """
        self.ensure_one()
        state = dict(picking._fields.get("state").selection).get(picking.state)
        return self.user_ids.sudo().notify_info(
            message=self.message
            or _("Picking changed status to '%(state)s'.", state=state),
            title=picking.name,
            sticky=True,
            action={
                "type": "ir.actions.act_window",
                "name": picking.name,
                "res_model": "stock.picking",
                "res_id": picking.id,
                "view_mode": "form",
                "view_type": "form",
                "target": "current",
            },
            sound=self._get_sound_path(),
        )
