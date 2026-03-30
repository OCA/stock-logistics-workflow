# Copyright 2020 Camptocamp SA
# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _after_apply_source_relocate_rule(self):
        super()._after_apply_source_relocate_rule()
        result = self._chain_apply_routing()
        _logger.debug("Dynamic routing applied on relocated moves %s", self.ids)
        return result
