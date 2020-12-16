# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _assign_picking_group_domain(self):
        domain = super()._assign_picking_group_domain()
        by_date_domain = self._assign_picking_group_domain_by_date()
        domain.extend(by_date_domain)
        return domain

    def _skip_assign_picking_group_domain_by_date(self):
        return (
            not self.picking_type_id.group_pickings_by_date
            or not self.picking_type_id.group_pickings
            or self.group_id.sale_id.picking_policy == "one"
            or self.env.context.get("picking_manual_merge")
        )

    def _assign_picking_group_domain_by_date(self):
        domain = []
        if self._skip_assign_picking_group_domain_by_date():
            return domain
        date_planned = self.date_expected
        date_planned_end = date_planned.replace(hour=23, minute=59, second=59)
        domain = [
            ("scheduled_date", "<=", date_planned_end),
            ("scheduled_date", ">=", date_planned),
        ]
        return domain
