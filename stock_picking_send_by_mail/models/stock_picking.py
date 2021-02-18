# Copyright 2015 - Sandra Figueroa Varela
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_picking_send(self):
        self.ensure_one()
        template = self.env.ref(
            "stock_picking_send_by_mail.email_template_stock_picking", False,
        )
        compose_form = self.env.ref("mail.email_compose_message_wizard_form", False,)
        ctx = dict(
            default_model="stock.picking",
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode="comment",
            user_id=self.env.user.id,
        )
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
