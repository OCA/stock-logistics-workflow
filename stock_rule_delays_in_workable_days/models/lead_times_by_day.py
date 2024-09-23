# Copyright 2024 Foodles (https://www.foodles.co/).
# @author Alexandre Galdeano <alexandre.galdeano@foodles.co>
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models

from .weekday import WeekdaysEnum


class LeadTimesByDay(models.Model):
    _name = "lead_times_by_day"
    _description = "Lead times by day"

    _order = "weekday"

    weekday = fields.Selection(
        WeekdaysEnum.selection(),
        string="Purchase weekday",
        required=True,
        help="Days of weeks to purchase/order goods",
    )

    value_ids = fields.Many2many(
        "lead_times_by_day.value",
        string="Lead days",
        required=True,
        help="List of received lead days according the purchase weekday.",
    )

    rule_id = fields.Many2one("stock.rule", string="Rule")
