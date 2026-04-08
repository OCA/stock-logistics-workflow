# Copyright 2020 Camptocamp SA
# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _after_apply_dynamic_routing_rule(self):
        self.with_context(bypass_log_message=True)._apply_source_relocate()
        return self.with_context(exclude_apply_source_relocate=True)

    def _after_apply_source_relocate_rule(self, merge=True):
        # Apply dynamic routing on relocated move to potentially route it in
        # another picking
        _logger.debug(f"Apply dynamic routing on relocated moves {self}")
        self._chain_apply_routing()
        super()._after_apply_source_relocate_rule(merge=merge)
        return
