# Copyright (C) 2023-Today:
# Dinamiche Aziendali Srl (<http://www.dinamicheaziendali.it/>)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Giuseppe Borruso <gborruso@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

logger = logging.getLogger(__name__)


class StockClosePeriodLineInherit(models.Model):
    _inherit = "stock.close.period.line"

    evaluation_method = fields.Selection(selection_add=[("production", "Production")])
