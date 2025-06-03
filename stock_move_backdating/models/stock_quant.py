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
        quantity=False,
        reserved_quantity=False,
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
            quantity=quantity,
            reserved_quantity=reserved_quantity,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            in_date=in_date,
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
        """
        Returns a list of fields user can edit when editing a quant in `inventory_mode`.
        """
        res = super()._get_inventory_fields_write()
        res += ["date_backdating"]
        return res

    def _get_inventory_move_values(
        self,
        qty,
        location_id,
        location_dest_id,
        package_id=False,
        package_dest_id=False,
    ):
        """Override to add backdating date to move lines if applicable"""
        res = super()._get_inventory_move_values(
            qty,
            location_id,
            location_dest_id,
            package_id=package_id,
            package_dest_id=package_dest_id,
        )

        date_backdating = self.env.context.get("date_backdating", False)

        if date_backdating:
            if "move_line_ids" in res and isinstance(res["move_line_ids"], list):
                new_move_line_ids = []
                for line_command in res["move_line_ids"]:
                    if (
                        isinstance(line_command, tuple | list)
                        and len(line_command) == 3
                        and line_command[0] == 0
                    ):
                        line_values = line_command[2]
                        # Add the backdating date to the move line values
                        line_values["date_backdating"] = date_backdating
                        new_move_line_ids.append((0, 0, line_values))
                    else:
                        new_move_line_ids.append(line_command)
                res["move_line_ids"] = new_move_line_ids

        return res
