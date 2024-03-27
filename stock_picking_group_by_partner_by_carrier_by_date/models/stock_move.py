# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import models

from odoo.addons.partner_tz.tools.tz_utils import (
    tz_to_utc_naive_datetime,
    utc_to_tz_naive_datetime,
)


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
        tz = (
            self.warehouse_id.partner_id.tz
            or self.env.company.partner_id.tz
            or self.env.user.tz
        )
        date_tz = utc_to_tz_naive_datetime(tz, self.date)
        dt_start_tz = date_tz.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        dt_start = tz_to_utc_naive_datetime(tz, dt_start_tz)
        dt_end = dt_start + timedelta(days=1)
        domain = [
            ("scheduled_date", "<", dt_end),
            ("scheduled_date", ">=", dt_start),
        ]
        return domain
