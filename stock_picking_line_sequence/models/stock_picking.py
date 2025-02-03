# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from lxml import etree

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.depends("move_ids_without_package")
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence entered in move lines.
        Then we add 1 to this value for the next sequence, this value is
        passed to the context of the o2m field in the view.
        So when we create new move line, the sequence is automatically
        incremented by 1. (max_sequence + 1)
        """
        for picking in self:
            picking.max_line_sequence = (
                max(picking.mapped("move_ids_without_package.sequence") or [0]) + 1
            )

    max_line_sequence = fields.Integer(
        string="Max sequence in lines", compute="_compute_max_line_sequence"
    )

    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.move_ids_without_package:
                # Check if the record ID is an integer (real ID)
                # or a string (virtual ID)
                if isinstance(line.id, int):
                    line.sequence = current_sequence
                    current_sequence += 1

    def copy(self, default=None):
        return super(StockPicking, self.with_context(keep_line_sequence=True)).copy(
            default
        )

    def button_validate(self):
        return super(
            StockPicking, self.with_context(keep_line_sequence=True)
        ).button_validate()

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """Append the default sequence.

        The context of `move_ids_without_package` is already overloaded
        and replacing it in a view does not scale across other extension
        modules.
        """
        res = super().get_view(view_id=view_id, view_type=view_type, **options)

        if res.get("arch") and view_type == "form":
            doc = etree.XML(res["arch"])
            elements = doc.xpath("//field[@name='move_ids_without_package']")
            if elements:
                element = elements[0]
                context = element.get("context", "{}")
                context = "{}{}, {}".format(
                    context[0], "'default_sequence': max_line_sequence", context[1:]
                )
                element.set("context", context)
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
