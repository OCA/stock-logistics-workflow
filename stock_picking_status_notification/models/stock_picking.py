# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, registry


class StockPicking(models.Model):
    _inherit = "stock.picking"

    to_web_notify = fields.Boolean(
        default=False,
        help="Technical field for storing the “to notify” attribute, "
        "which is used to retrieve all records for this attribute "
        "and to send a notification.",
    )

    def _write_multi(self, vals_list):
        new_vals = list()
        for vals in vals_list:
            if "state" in vals:
                vals = dict(vals)
                vals.setdefault("to_web_notify", True)
            new_vals.append(vals)

        dbname = self.env.cr.dbname
        context = self.env.context
        uid = self.env.uid
        res = super()._write_multi(new_vals)

        # only the latest state needs to be sent
        @self.env.cr.postcommit.add
        def trigger_picking_notification():
            db_registry = registry(dbname)
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
