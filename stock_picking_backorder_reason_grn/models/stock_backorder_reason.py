# Copyright 2017 Camptocamp SA
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockBackorderReason(models.Model):

    _inherit = "stock.backorder.reason"

    keep_grn = fields.Boolean(
        help="Check this if you want to keep the Goods Received Note from picking"
        "to backorder when using this reason."
    )
