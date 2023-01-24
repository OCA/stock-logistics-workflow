# Copyright 2017 Camptocamp SA
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockBackorderReason(models.Model):

    _name = "stock.backorder.reason"
    _description = "Stock Backorder Reason"

    name = fields.Char(required=True, translate=True)
    backorder_action_to_do = fields.Selection(
        selection=[
            ("create", "Create backorder"),
            ("cancel", "Cancel backorder"),
            ("use_partner_option", "Use partner option"),
        ],
        default="picking_type",
    )
