# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import _, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_deposit_count = fields.Integer(compute="_compute_customer_deposit_count")

    def _compute_customer_deposit_count(self):
        for partner in self:
            partner.customer_deposit_count = self.env["stock.quant"].search_count(
                partner._get_customer_deposit_domain()
            )

    def _get_customer_deposit_domain(self):
        return [
            ("location_id.usage", "=", "internal"),
            ("quantity", ">", 0),
            "|",
            "|",
            ("owner_id", "=", self.id),
            ("owner_id", "parent_of", self.ids),
            ("owner_id", "child_of", self.ids),
        ]

    def action_view_customer_deposits(self):
        action = (
            self.env["stock.quant"]
            .with_context(no_at_date=True, search_default_on_hand=True)
            ._get_quants_action(self._get_customer_deposit_domain())
        )
        action["name"] = _("Customer Deposits")
        return action
