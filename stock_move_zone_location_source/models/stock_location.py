# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockLocation(models.Model):

    _inherit = "stock.location"

    is_considered_as_source = fields.Boolean(
        index=True,
        compute="_compute_is_considered_as_source",
        store=True,
        readonly=False,
        help="Check this to consider this picking type as the source one for "
        "the moves later in the flow.",
    )

    @api.depends("is_zone")
    def _compute_is_considered_as_source(self):
        # Reset value if is_zone field is set to False
        self.filtered(lambda location: location.is_zone).update(
            {"is_considered_as_source": False}
        )

    def _get_source_zone(self):
        """
        Return all parents from this recordset considered as source.

        Do it through a search on the whole recordset for performance reasons,
        then, manage the result with filtered() or...
        """
        zones = self.search(
            [("id", "parent_of", self.ids), ("is_considered_as_source", "=", True)]
        )
        source_zones = self.browse()
        for location in self:
            location_zones = zones.filtered_domain([("id", "parent_of", location.id)])
            the_zone = self.browse()
            for location_zone in location_zones:
                if the_zone:
                    if len(location_zone.parent_path) > len(the_zone.parent_path):
                        the_zone = location_zone
                else:
                    the_zone = location_zone
            source_zones |= the_zone
        return source_zones
