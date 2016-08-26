# -*- coding: utf-8 -*-
# © 2012-2014 Nicolas Bessi, Joel Grand-Guillaume, Alexandre Fayolle
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from openerp import models

from print_batch import PrintBatch


_logger = logging.getLogger(__name__)


class ReportPrintBatchPicking(models.AbstractModel):
    _name = 'report.stock_batch_picking.report_batch_picking'
    _inherit = 'report.abstract_report'
    _template = 'stock_batch_picking.report_batch_picking'
    _wrapped_report_class = PrintBatch
