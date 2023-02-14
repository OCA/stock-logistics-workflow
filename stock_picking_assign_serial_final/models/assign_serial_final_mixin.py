# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re

from odoo import api, fields, models


class AssignSerialFinalMixin(models.AbstractModel):
    _name = "assign.serial.final.mixin"
    _description = "Mixin for assign last S/N"
    _next_serial_field = ""

    final_serial_number = fields.Char("Final SN")
    next_serial_count = fields.Integer(
        compute="_compute_next_serial_count",
        store=True,
        readonly=False,
    )

    @api.depends(lambda x: x._get_next_serial_depends())
    def _compute_next_serial_count(self):
        for rec in self:
            if not (rec[rec._next_serial_field] and rec.final_serial_number):
                rec.next_serial_count = 0
                continue
            lot_search = re.search(r"-?\d+\.?\d*", rec[rec._next_serial_field])
            start_num = lot_search.group()
            lot_search_to = re.search(r"-?\d+\.?\d*", rec.final_serial_number)
            end_num = lot_search_to.group()
            if start_num and end_num:
                rec.next_serial_count = int(end_num) - int(start_num) + 1
            else:
                rec.next_serial_count = 0

    @api.model
    def _get_next_serial_depends(self):
        if not self._next_serial_field:
            return []
        return [self._next_serial_field, "final_serial_number"]
