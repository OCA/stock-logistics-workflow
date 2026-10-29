# Copyright 2017 Camptocamp SA
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_reason_backorder_strategy = fields.Selection(
        selection=[("create", "Create"), ("cancel", "Cancel")],
        default=lambda self: self._get_default_sale_reason_backorder_strategy(),
        required=True,
        tracking=True,
        help="Choose the strategy that will be applied on pickings that have "
        "backorder choice enabled and depending on partner sale strategy.",
    )
    purchase_reason_backorder_strategy = fields.Selection(
        selection=[("create", "Create"), ("cancel", "Cancel")],
        default=lambda self: self._get_default_purchase_reason_backorder_strategy(),
        required=True,
        tracking=True,
        help="Choose the strategy that will be applied on pickings that have "
        "backorder choice enabled and depending on partner purchase strategy.",
    )

    @api.model
    def _get_default_sale_reason_backorder_strategy(self):
        return self.env.company.partner_sale_backorder_default_strategy

    @api.model
    def _get_default_purchase_reason_backorder_strategy(self):
        return self.env.company.partner_purchase_backorder_default_strategy
