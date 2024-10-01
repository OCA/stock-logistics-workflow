# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.constrains("lot_name", "lot_id")
    def _check_serial_number(self):
        """This method intends to check and make sure that the stock
        for specified serial does not exist.
        The check is expected to be triggered when:
        - user inputs serial (in lot_name) in purchase receipt / manufacturing order
        - serial record (stock.lot) is being created in _action_done()
        """
        for record in self:
            if (
                (record.lot_id or record.lot_name)
                and record.product_id.tracking == "serial"
                # Check should be done only in the scenario where new serial is created.
                and record.picking_type_id.use_create_lots
            ):
                lot_id = record.lot_id
                if not lot_id:
                    lot_id = self.env["stock.lot"].search(
                        [
                            ("product_id", "=", record.product_id.id),
                            ("name", "=", record.lot_name),
                            ("company_id", "=", record.company_id.id),
                        ]
                    )
                message, dummy = self.env["stock.quant"]._check_serial_number(
                    record.product_id,
                    lot_id,
                    record.company_id,
                )
                if message:
                    raise ValidationError(_(message))
