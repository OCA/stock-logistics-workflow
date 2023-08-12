# Copyright 2020 Camptocamp SA
# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _apply_source_relocate_rule(self, relocation, reserved_availability, roundings):
        relocated = super(
            StockMove,
            # disable application of routing in write() method of
            # stock_dynamic_routing, we'll apply it here whatever the state of
            # the move is
            self.with_context(__applying_routing_rule=True),
        )._apply_source_relocate_rule(relocation, reserved_availability, roundings)
        # restore the previous context without "__applying_routing_rule", otherwise
        # it wouldn't properly apply the routing in chain in the further moves
        relocated = relocated.with_context(self.env.context)
        return relocated

    def _after_apply_source_relocate_rule(self):
        super()._after_apply_source_relocate_rule()
        result = self._chain_apply_routing()
        _logger.debug("Dynamic routing applied on relocated moves %s" % self.ids)
        return result
