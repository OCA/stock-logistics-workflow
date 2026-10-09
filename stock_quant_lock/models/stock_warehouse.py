# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    quality_check_route_id = fields.Many2one(
        comodel_name="stock.route",
        string="Quality Check Route",
        help="Default route used to lock the quants of the warehouse for a "
        "quality check.",
        check_company=True,
        ondelete="restrict",
    )

    @api.model_create_multi
    def create(self, vals_list):
        warehouses = super().create(vals_list)
        warehouses._create_quality_check_lock()
        return warehouses

    def _create_quality_check_lock(self):
        """Create the records needed to lock quants for a quality check."""
        for warehouse in self.filtered(lambda wh: not wh.quality_check_route_id):
            location = self.env["stock.location"].create(
                warehouse._prepare_quality_check_location_values()
            )
            picking_type = self.env["stock.picking.type"].create(
                warehouse._prepare_quality_check_type_values(location)
            )
            warehouse.quality_check_route_id = self.env["stock.route"].create(
                warehouse._prepare_quality_check_route_values(location, picking_type)
            )

    def _prepare_quality_check_location_values(self):
        self.ensure_one()
        return {
            "name": _("Quality Check"),
            "usage": "internal",
            "location_id": self.view_location_id.id,
            "company_id": self.company_id.id,
            "barcode": self._valid_barcode(self.code + "-QC", self.company_id.id),
        }

    def _prepare_quality_check_type_values(self, location):
        self.ensure_one()
        sequence = (
            self.env["ir.sequence"]
            .sudo()
            .create(
                {
                    "name": "%s %s" % (self.name, _("Quality Check Sequence")),
                    "prefix": "%s/QC/" % self.code,
                    "padding": 5,
                    "company_id": self.company_id.id,
                }
            )
        )
        return {
            "name": _("Quality Check"),
            "code": "internal",
            "sequence_code": "QC",
            "sequence_id": sequence.id,
            "use_create_lots": False,
            "use_existing_lots": True,
            "default_location_src_id": self.lot_stock_id.id,
            "default_location_dest_id": location.id,
            "show_reserved": True,
            "show_operations": True,
            "warehouse_id": self.id,
            "company_id": self.company_id.id,
        }

    def _prepare_quality_check_route_values(self, location, picking_type):
        self.ensure_one()
        return {
            "name": self._format_routename(name=_("Quality Check")),
            "allow_quant_lock": True,
            "product_selectable": False,
            "company_id": self.company_id.id,
            "sequence": 10,
            "rule_ids": [
                (0, 0, self._prepare_quality_check_rule_values(location, picking_type))
            ],
        }

    def _prepare_quality_check_rule_values(self, location, picking_type):
        self.ensure_one()
        return {
            "name": self._format_rulename(self.view_location_id, location, ""),
            "action": "pull",
            "procure_method": "make_to_stock",
            "location_src_id": self.view_location_id.id,
            "location_dest_id": location.id,
            "picking_type_id": picking_type.id,
            "warehouse_id": self.id,
            "company_id": self.company_id.id,
        }
