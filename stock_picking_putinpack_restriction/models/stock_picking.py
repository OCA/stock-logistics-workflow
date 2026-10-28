# Copyright 2023 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    put_in_pack_restriction = fields.Selection(
        related="picking_type_id.put_in_pack_restriction"
    )

    def _pre_put_in_pack_hook(self, move_line_ids):
        # All put in pack paths go through this hook: transfer, move lines,
        # batch transfer and the package destination wizard. In a batch, the
        # move lines can come from several transfers, so check all of them.
        picking_types = self.picking_type_id | move_line_ids.picking_id.picking_type_id
        forbidden = picking_types.filtered(
            lambda picking_type: picking_type.put_in_pack_restriction == "no_package"
        )
        if forbidden:
            raise ValidationError(
                _(
                    "Destination package can not be used with "
                    "%(picking_type_name)s transfer.",
                    picking_type_name=", ".join(forbidden.mapped("name")),
                )
            )
        return super()._pre_put_in_pack_hook(move_line_ids)
