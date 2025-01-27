# Copyright 2025 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models
from odoo.osv.expression import AND


class StockMove(models.Model):
    _inherit = "stock.move"

    def _skip_assign_picking_group_domain_by_release_blocked(self):
        return not self.picking_type_id.group_pickings_by_release_blocked

    def _search_picking_for_assignation_domain(self):
        if self._skip_assign_picking_group_domain_by_release_blocked():
            return super()._search_picking_for_assignation_domain()
        res = AND(
            [
                super()._search_picking_for_assignation_domain(),
                [("release_blocked", "=", self.release_blocked)],
            ]
        )
        return res

    def _key_assign_picking(self):
        keys = super()._key_assign_picking()
        return keys + (self.release_blocked,)
