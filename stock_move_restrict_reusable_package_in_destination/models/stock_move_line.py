# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
import traceback

from odoo import _, api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.constrains("result_package_id")
    def _check_reusable_package_restriction(self):
        for line in self.filtered(
            "picking_type_id.restrict_reusable_package_in_destination"
        ):
            package_name = line.result_package_id.name
            picking_name = line.picking_id.name
            raise ValidationError(
                _(
                    "You cannot put the reusable package (%(package_name)s) in picking"
                    " (%(picking_name)s)! Check with your administrator.",
                    package_name=package_name,
                    picking_name=picking_name,
                )
            )

        for line in self.filtered(
            "picking_type_id.log_warning_reusable_package_in_destination"
        ):
            package_name = line.result_package_id.name
            picking_name = line.picking_id.name
            warning_message = _(
                "You cannot put the reusable package (%(package_name)s) in picking"
                " (%(picking_name)s)! Check with your administrator.",
                package_name=package_name,
                picking_name=picking_name,
            )
            warning_message += "\n"
            warning_message += "\n".join(traceback.format_stack())
            _logger.warning(warning_message)
