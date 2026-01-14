# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

import pytz

from odoo import fields, models
from odoo.fields import Domain
from odoo.tools import date_utils, format_date


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_batch_group_by_date_tz(self) -> str:
        """Get the timezone to use for the batch group by date"""
        self.ensure_one()
        return (
            self.move_ids.warehouse_id.partner_id.tz
            or self.env.company.partner_id.tz
            or self.env.user.tz
            or "UTC"
        )

    def _get_batch_group_by_date_limits(self) -> tuple[datetime, datetime]:
        """Get the datetime limits for the batch group by date"""
        self.ensure_one()
        tz = self._get_batch_group_by_date_tz()
        timezone = pytz.timezone(tz)
        date_tz = fields.Datetime.context_timestamp(
            self.with_context(tz=tz),
            self.scheduled_date,
        )
        to_utc = date_utils.to_timezone(None)
        from_date_tz = timezone.localize(fields.Datetime.start_of(date_tz, "day"))
        to_date_tz = timezone.localize(fields.Datetime.end_of(date_tz, "day"))
        return to_utc(from_date_tz), to_utc(to_date_tz)

    def _get_possible_pickings_domain(self):
        domain = super()._get_possible_pickings_domain()
        if self.picking_type_id.batch_group_by_date:
            from_date, to_date = self._get_batch_group_by_date_limits()
            domain &= Domain("scheduled_date", ">=", from_date)
            domain &= Domain("scheduled_date", "<=", to_date)
        return domain

    def _get_possible_batches_domain(self):
        domain = super()._get_possible_batches_domain()
        if self.picking_type_id.batch_group_by_date:
            from_date, to_date = self._get_batch_group_by_date_limits()
            domain &= Domain("scheduled_date", ">=", from_date)
            domain &= Domain("scheduled_date", "<=", to_date)
        return domain

    def _get_auto_batch_description(self):
        description = super()._get_auto_batch_description()
        if self.picking_type_id.batch_group_by_date:
            tz = self._get_batch_group_by_date_tz()
            env_tz = self.with_context(tz=tz).env
            date_str = format_date(env_tz, self.scheduled_date)
            description = f"{description}, {date_str}" if description else date_str
        return description
