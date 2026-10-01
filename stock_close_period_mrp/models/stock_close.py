# Copyright (C) 2023-Today:
# Dinamiche Aziendali Srl (<http://www.dinamicheaziendali.it/>)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Giuseppe Borruso <gborruso@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class StockClosePeriodInherit(models.Model):
    _inherit = "stock.close.period"

    force_standard_price = fields.Boolean(
        default=False,
        help="Forces the use of the standard price instead of calculating the cost "
        "from the BOM.",
    )
    production_ok = fields.Boolean(
        default=False,
        readonly=True,
        help="Marks if action 'Compute Production' is processed.",
    )

    def action_set_to_draft(self):
        res = super(StockClosePeriodInherit, self).action_set_to_draft()
        for closing in self:
            closing.production_ok = False
        return res

    def action_recalculate_production(self):
        for closing in self:
            if not closing.bypass_negative_qty and not closing._check_qty_available():
                raise UserError(
                    _(
                        "Is not possible continue the execution. There are product "
                        "with quantities < 0."
                    )
                )

            self.env["stock.move.line"].recompute_average_cost_period_production(
                closing
            )
            closing.production_ok = True
            if closing.force_archive:
                closing._deactivate_moves()
            closing.work_end = datetime.now()
        return True
