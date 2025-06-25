# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.osv.expression import AND


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def _get_location_destination_move_line_suggestion_domain(self):
        domain = super()._get_location_destination_move_line_suggestion_domain()
        if self.picking_type_id.suggest_destination_release_channel:
            domain = AND(
                [
                    domain,
                    [
                        (
                            "picking_id.release_channel_id",
                            "in",
                            (
                                self.release_channel_id
                                | self.move_ids.move_dest_ids.picking_id.release_channel_id
                            ).ids,
                        )
                    ],
                ]
            )
        return domain
