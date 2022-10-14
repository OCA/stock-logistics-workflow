# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.fields import first


class StockLocation(models.Model):
    _inherit = "stock.location"

    @property
    def _putaway_strategies(self):
        """List of plugged put-away strategies

        Each item is the key of the strategy. When applying the putaway, if no
        strategy is found for the product and the category (default ones), the
        method ``_alternative_putaway_strategy`` will loop over these keys.

        The key of a strategy must be the name of the field added on
        ``stock.putaway.rule``.

        For instance if the strategies are ["route_id", "foo"], the putaway will:

        * search a putaway for the product (core module)
        * if not found, search for the product category (core module)

        If None is found, the alternatives strategies are looked for:

        * if not found, search for route_id
        * if not found, search for foo
        """
        return []

    def _get_putaway_strategy(
        self, product, quantity=0, package=None, packaging=None, additional_qty=None
    ):
        """Extend the code method to add hooks

        * Call the alternative strategies lookups
        * Call a hook ``_putaway_strategy_finalizer`` after all the strategies
        * This should always return a result
        """
        putaway_location = super()._get_putaway_strategy(
            product, quantity, package, packaging, additional_qty
        )
        if putaway_location == self:
            putaway_location = self._alternative_putaway_strategy()
        return self._putaway_strategy_finalizer(
            putaway_location, product, quantity, package, packaging, additional_qty
        )

    def _alternative_putaway_strategy(self):
        """Find a putaway according to the ``_putaway_strategies`` keys

        The methods that calls ``StockLocation._get_putaway_strategy have to
        pass in the context a key with the name ``_putaway_<KEY>``, where KEY
        is the name of the strategy. The value must be the value to match with
        the putaway rule. The value can be a unit, a recordset of any length or
        a list/tuple. In latter cases, the putaway rule is selected if its
        field match any value in the list/recordset.
        """
        current_location = self
        putaway_location = self.browse()

        strategy_values = {
            field: self.env.context.get("_putaway_{}".format(field))
            for field in self._putaway_strategies
        }

        # retain only the strategies for which we have a value provided in context
        available_strategies = [
            strategy
            for strategy in self._putaway_strategies
            if strategy_values.get(strategy)
        ]

        if not available_strategies:
            return current_location

        while current_location and not putaway_location:
            # copy and reverse the strategies, so we pop them in their order
            strategies = available_strategies[::-1]
            while not putaway_location and strategies:
                strategy = strategies.pop()
                value = strategy_values[strategy]
                # Looking for a putaway from the strategy
                putaway_rules = current_location.putaway_rule_ids.filtered(
                    lambda x: x[strategy] in value
                    if isinstance(value, (models.BaseModel, list, tuple))
                    else x[strategy] == value
                )
                putaway_location = first(putaway_rules).location_out_id
            current_location = current_location.location_id
        return putaway_location or self

    def _putaway_strategy_finalizer(
        self,
        putaway_location,
        product,
        quantity=0,
        package=None,
        packaging=None,
        additional_qty=None,
    ):
        """Hook for putaway called after the strategy lookup"""
        # by default, do nothing
        return putaway_location
