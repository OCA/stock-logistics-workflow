# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


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
        relocated.with_context(self.env.context)._chain_apply_routing()
        return relocated
