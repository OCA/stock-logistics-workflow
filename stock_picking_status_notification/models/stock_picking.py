# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.modules.registry import Registry


class StockPicking(models.Model):
    _inherit = "stock.picking"

    to_web_notify = fields.Boolean(
        default=False,
        help="Technical field for storing the “to notify” attribute, "
        "which is used to retrieve all records for this attribute "
        "and to send a notification.",
    )

    def _compute_state(self):
        res = super()._compute_state()
        templates_per_picking = self.env[
            "stock.picking.notification.template"
        ]._get_matching_templates(self)
        for picking in self:
            if picking in templates_per_picking:
                picking.to_web_notify = True

        dbname = self.env.cr.dbname
        context = self.env.context
        uid = self.env.uid

        @self.env.cr.postcommit.add
        def trigger_picking_notification():
            db_registry = Registry(dbname)
            with db_registry.cursor() as cr:
                env = api.Environment(cr, uid, context)
                to_notify = env["stock.picking"].search([("to_web_notify", "=", True)])
                if to_notify:
                    to_notify.sudo()._trigger_picking_notification()
                    to_notify.to_web_notify = False

        return res

    def _trigger_picking_notification(self):
        """
        Check notification rules and trigger notifications if conditions are met.
        """
        notify_template_obj = self.env["stock.picking.notification.template"]
        for picking in self:
            template = notify_template_obj._get_matching_template(picking)
            if template:
                template._notify_picking_users(picking)
