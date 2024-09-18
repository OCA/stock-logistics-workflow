# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    lot_life_date = fields.Datetime(string="Lot/Serial End of Life Date")
    lot_use_date = fields.Datetime(string="Lot/Serial Best before Date")
    lot_removal_date = fields.Datetime(string="Lot/Serial Removal Date")
    lot_alert_date = fields.Datetime(string="Lot/Serial Alert Date")

    def _prepare_new_lot_vals(self):
        vals = super()._prepare_new_lot_vals()
        creation_lot_fields = ["life_date", "use_date", "removal_date", "alert_date"]
        for field in creation_lot_fields:
            value = getattr(self, "lot_" + field)
            if value:
                vals[field] = fields.Datetime.to_string(value)
        return vals
