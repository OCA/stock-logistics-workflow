# Copyright (C) 2023-Today:
# Dinamiche Aziendali Srl (<http://www.dinamicheaziendali.it/>)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Giuseppe Borruso <gborruso@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_additional_landed_cost_new(self, move_id, company_id):
        additional_landed_cost_new = super()._get_additional_landed_cost_new(
            move_id=move_id, company_id=company_id
        )
        svals = (
            self.env["stock.valuation.adjustment.lines"]
            .sudo()
            .search(
                [
                    ("move_id", "=", move_id.id),
                    ("cost_id.company_id", "=", company_id),
                ]
            )
        )
        if svals:
            additional_landed_cost_new = sum(svals.mapped("additional_landed_cost"))
        return additional_landed_cost_new
