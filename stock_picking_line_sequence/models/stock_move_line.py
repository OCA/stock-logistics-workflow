# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_aggregated_product_quantities(self, **kwargs):
        aggregated_move_lines = super()._get_aggregated_product_quantities(**kwargs)
        for move_line in self:
            line_key = self._get_aggregated_properties(move_line=move_line)["line_key"]
            sequence2 = move_line.move_id.sequence2
            if line_key in aggregated_move_lines:
                aggregated_move_lines[line_key]["sequence2"] = sequence2

        return aggregated_move_lines
