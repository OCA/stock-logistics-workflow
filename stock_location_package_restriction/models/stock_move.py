# Copyright 2023 Raumschmiede (http://www.raumschmiede.de)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools import groupby

from .stock_location import NORESTRICTION, SINGLEPACKAGE


class StockMove(models.Model):
    _inherit = "stock.move"

    def _check_location_package_restriction(self):
        """
        Check if the current stock.move can be executed
        regarding a potential package restriction
        """
        Package = self.env["stock.quant.package"]
        error_msgs = []
        quants_grouped = self.env["stock.quant"].read_group(
            [
                ("location_id", "in", self.move_line_ids.location_dest_id.ids),
                ("location_id.package_restriction", "!=", NORESTRICTION),
                ("quantity", ">", 0),
            ],
            ["location_id", "package_id:array_agg"],
            "location_id",
        )
        location_packages = {
            g["location_id"][0]: set(g["package_id"]) for g in quants_grouped
        }
        for location, move_lines in groupby(
            self.move_line_ids, lambda m: m.location_dest_id
        ):
            if location.package_restriction == NORESTRICTION:
                continue

            existing_package_ids = location_packages.get(location.id, set())
            existing_packages = Package.browse(existing_package_ids).exists()
            new_packages = Package.browse()
            for move_line in move_lines:
                package = move_line.result_package_id
                # CASE: Package restiction exists but there is no package in move
                if not package:
                    error_msgs.append(
                        _(
                            "The location {location} requires at least one Package. "
                            "You plan to move a Product without a Package."
                        ).format(location=location.name)
                    )
                    continue
                if location.package_restriction != SINGLEPACKAGE:
                    continue
                # CASE: Package on location, new package is different
                if existing_package_ids and package.id not in existing_package_ids:
                    error_msgs.append(
                        _(
                            "The location {location} already has a package on it "
                            "({existing_packages}) "
                            "but specifies single Package only."
                            "You try to put a different one on it ({package})."
                        ).format(
                            location=location.display_name,
                            existing_packages=", ".join(
                                existing_packages.mapped("name")
                            ),
                            package=package.display_name,
                        )
                    )
                    continue
                # CASE: Multiple packages in Move but single location
                # with singlepackage Restriction
                if new_packages and package not in new_packages:
                    error_msgs.append(
                        _(
                            "The location {location} "
                            "can only contain exactly one Package "
                            "at the same time. "
                            "You plan to move multiple packages to "
                            "this location. ({packages})"
                        ).format(
                            location=location.display_name,
                            packages=", ".join(new_packages.mapped("display_name")),
                        )
                    )
                    continue
                new_packages |= package

        if error_msgs:
            raise ValidationError("\n".join(error_msgs))

    def _action_done(self, cancel_backorder=False):
        self._check_location_package_restriction()
        return super()._action_done(cancel_backorder=cancel_backorder)
