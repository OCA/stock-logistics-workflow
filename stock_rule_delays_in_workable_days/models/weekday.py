# Copyright 2024 Foodles (https://www.foodles.co/).
# @author Alexandre Galdeano <alexandre.galdeano@foodles.co>
# @author Damien Crier <damien.crier@foodles.co>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import enum

from odoo import fields, models


@enum.unique
class WeekdaysEnum(enum.Enum):
    Monday = "0"
    Tuesday = "1"
    Wednesday = "2"
    Thursday = "3"
    Friday = "4"
    Saturday = "5"
    Sunday = "6"

    @classmethod
    def selection(cls):
        return [(member.value, member.name) for member in cls]

    @classmethod
    def from_weekday(cls, weekday: int) -> "WeekdaysEnum":
        return WeekdaysEnum(str(weekday % 7))

    def weekday(self) -> int:
        return int(self.value)

    @property
    def day_label(self):
        """
        Return the lowercase version of the label

        For example: Weekdays.Tuesday.day_label == "tuesday"
        """
        return self.name.lower()


class Weekdays(models.Model):
    _name = "weekdays"
    _description = "Model representing days in Odoo"

    name = fields.Char(required=True, translate=True)
    weekday = fields.Selection(selection=WeekdaysEnum.selection(), required=True)

    _sql_constraints = [
        (
            "weekday_uniq",
            "UNIQUE(weekday)",
            "Weekday must be unique!",
        ),
    ]
