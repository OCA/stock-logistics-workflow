# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    force_date = fields.Datetime(
        help="Force the moves to a given date.",
    )

    @api.model
    def create(self, vals):
        force_date = vals.get("force_date", False) or self.force_date
        if force_date and "in_date" in vals.keys():
            vals["in_date"] = force_date
        return super().create(vals)

    def write(self, vals):
        force_date = vals.get("force_date", False) or self.force_date
        if force_date and "in_date" in vals.keys():
            vals["in_date"] = force_date
        return super().write(vals)

    def _apply_inventory(self):
        res = super()._apply_inventory()
        self.write({"force_date": False})
        return res

    @api.model
    def _get_inventory_fields_write(self):
        """Returns a list of fields user can edit when editing a quant in `inventory_mode`."""
        res = super()._get_inventory_fields_write()
        res += ["force_date"]
        return res

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        res = super()._get_inventory_move_values(
            qty, location_id, location_dest_id, out
        )
        res["force_date"] = self.force_date
        return res
