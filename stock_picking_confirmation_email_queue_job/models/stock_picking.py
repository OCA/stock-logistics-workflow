# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models

from odoo.addons.queue_job.job import identity_exact
from odoo.addons.queue_job.utils import must_run_without_delay


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _send_confirmation_email(self):
        # Only the email is delayed: other overrides of this method (e.g. the
        # carrier label of stock_delivery) must keep running synchronously.
        return super(
            StockPicking, self.with_context(stock_confirmation_email_delay=True)
        )._send_confirmation_email()

    def message_post_with_source(
        self,
        source_ref,
        render_values=None,
        message_type="notification",
        subtype_xmlid=False,
        subtype_id=False,
        **kwargs,
    ):
        post_kwargs = dict(
            kwargs,
            render_values=render_values,
            message_type=message_type,
            subtype_xmlid=subtype_xmlid,
            subtype_id=subtype_id,
        )
        if (
            self.env.context.get("stock_confirmation_email_delay")
            and not self.env.context.get("job_uuid")
            and not must_run_without_delay(self.env)
            and isinstance(source_ref, models.BaseModel)
            and source_ref._name == "mail.template"
            and source_ref in self.company_id.stock_mail_confirmation_template_id
        ):
            for picking in self:
                picking.with_delay(
                    description=self.env._(
                        "Send confirmation email of %s", picking.display_name
                    ),
                    identity_key=identity_exact,
                )._post_confirmation_email(
                    source_ref,
                    post_kwargs,
                    force_send=self.env.context.get("force_send"),
                )
            return self.env["mail.message"]
        return super().message_post_with_source(source_ref, **post_kwargs)

    def _post_confirmation_email(self, template, post_kwargs, force_send=False):
        return self.with_context(force_send=force_send).message_post_with_source(
            template, **post_kwargs
        )
