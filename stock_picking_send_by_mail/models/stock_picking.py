# Copyright 2015 - Sandra Figueroa Varela
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_email_sent = fields.Boolean()

    def _get_picking_send_email_template(self):
        return self.company_id.stock_mail_confirmation_template_id

    def _get_picking_send_composer_context(self, template_id):
        return dict(
            default_model=self._name,
            default_res_id=self.id,
            default_use_template=bool(template_id),
            default_template_id=template_id,
            default_composition_mode="comment",
            user_id=self.env.user.id,
        )

    def action_picking_send(self):
        """Send the shipping e-mail notification to the customer."""
        self.ensure_one()
        template = self._get_picking_send_email_template()
        compose_form = self.env.ref(
            "mail.email_compose_message_wizard_form",
            False,
        )
        template_id = template.id if template else False
        if self._check_send_delivery_email():
            return self._send_delivery_email(template_id)
        ctx = self._get_picking_send_composer_context(template_id)
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }

    def _check_send_delivery_email(self):
        return (
            self.partner_id.email
            and self.picking_type_id.send_delivery_email
            and not self.delivery_email_sent
        )

    def _send_delivery_email(self, template_id):
        """Send directly the notification e-mail to the customer."""
        ctx = self._get_picking_send_composer_context(template_id)
        wiz = self.env["mail.compose.message"].with_context(**ctx).create({})
        values = wiz.onchange_template_id(template_id, "comment", self._name, self.id)[
            "value"
        ]
        wiz.write(values)
        wiz.send_mail()
        self.delivery_email_sent = True
        return True
