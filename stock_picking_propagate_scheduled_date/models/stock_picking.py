# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _register_hook(self):
        # Patch `_action_done` to initialize `date_propagated_ids` in the context, so that   # noqa
        # it's available on the whole stack chain, independent of the MRO.
        #
        # This is required because some addons such as mrp_subcontracting will act on that  # noqa
        # method with a different context and we end up propagating the date changes more   # noqa
        # than once.
        res = super()._register_hook()

        def make_action_done():
            def _action_done(self, **kw):
                if "date_propagation_ids" not in self.env.context:
                    self = self.with_context(date_propagation_ids=set())
                return _action_done.origin(self, **kw)

            return _action_done

        patched_models = defaultdict(set)

        def patch(model, name, method):
            if model not in patched_models[name]:
                patched_models[name].add(model)
                ModelClass = model.env.registry[model._name]
                method.origin = getattr(ModelClass, name)
                setattr(ModelClass, name, method)

        patch(self, "_action_done", make_action_done())
        return res
