# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPutawayRule(models.Model):

    _inherit = "stock.putaway.rule"

    foo = fields.Boolean()


class StockLocation(models.Model):

    _inherit = "stock.location"

    @property
    def _putaway_strategies(self):
        strategies = super()._putaway_strategies
        return strategies + ["foo"]
