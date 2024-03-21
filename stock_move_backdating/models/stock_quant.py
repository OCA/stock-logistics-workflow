#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .stock_move_line import check_date


class StockQuant(models.Model):
    _inherit = "stock.quant"

    date_backdating = fields.Datetime(
        string="Actual Inventory Date",
    )

    @api.onchange("date_backdating")
    def onchange_date_backdating(self):
        self.ensure_one()
        check_date(self.date_backdating)

    @api.model
    def _update_available_quantity(
        self,
        product_id,
        location_id,
        quantity,
        lot_id=None,
        package_id=None,
        owner_id=None,
        in_date=None,
    ):
        date_backdating = self.env.context.get("date_backdating", False)
        if date_backdating:
            if in_date:
                in_date = min(date_backdating, in_date)
            else:
                in_date = date_backdating
        return super()._update_available_quantity(
            product_id,
            location_id,
            quantity,
            lot_id,
            package_id,
            owner_id,
            in_date,
        )

    def _apply_inventory(self):
        no_backdate_inventories = self.env["stock.quant"].browse()
        for inventory in self:
            date_backdating = inventory.date_backdating
            if date_backdating:
                inventory_ctx = inventory.with_context(
                    date_backdating=date_backdating,
                    force_period_date=fields.Date.context_today(self, date_backdating),
                )
                super(StockQuant, inventory_ctx)._apply_inventory()
                inventory.date_backdating = False
            else:
                no_backdate_inventories |= inventory
        return super(StockQuant, no_backdate_inventories)._apply_inventory()

    @api.model
    def _get_inventory_fields_write(self):
        """Returns a list of fields user can edit when editing a quant in `inventory_mode`."""
        res = super()._get_inventory_fields_write()
        res += ["date_backdating"]
        return res

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        res = super()._get_inventory_move_values(
            qty, location_id, location_dest_id, out
        )
        date_backdating = self.date_backdating
        if date_backdating:
            move_line_ids = res.get("move_line_ids", list())
            for move_line_values in move_line_ids:
                # Extract the dictionary from (0, 0, <dict>)
                move_line_values = move_line_values[2]
                move_line_values["date_backdating"] = date_backdating
        return res
