# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockWarehouse(models.Model):

    _inherit = "stock.warehouse"

    lot_remove_enabled = fields.Boolean(
        string="Enable Expired Lot Removal",
        help="If checked, a move will be planned reserving the expired lot.",
    )

    lot_remove_orig_location_ids = fields.Many2many(
        comodel_name="stock.location",
        string="Expired Lot Origin Locations",
        help="Locations from which expired lots will be moved.",
        compute="_compute_lot_remove_orig_location_ids",
        store=True,
        readonly=False,
    )

    lot_remove_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Expired Lot Move Picking Type",
        help="Picking type used for moving expired lots.",
    )

    @api.depends("lot_remove_enabled")
    def _compute_lot_remove_orig_location_ids(self):
        """Ensure that the origin and destination locations are set when
        enabling expired lot move."""
        for record in self:
            if record.lot_remove_enabled and not record.lot_remove_orig_location_ids:
                record.lot_remove_orig_location_ids = record.lot_stock_id

    @api.constrains("lot_remove_orig_location_ids", "lot_remove_enabled")
    def _check_expired_lot_locations(self):
        """Ensure that:
        * the origin location is set,
        * the origin location is from the current warehouse,
        """
        for record in self:
            if record.lot_remove_enabled:
                if not record.lot_remove_orig_location_ids:
                    raise ValidationError(
                        _(
                            "Please set at least one origin location for expired lot moves."
                        )
                    )
                if record.lot_remove_orig_location_ids.mapped("warehouse_id") != record:
                    raise ValidationError(
                        _(
                            "The origin locations for expired lot moves must be from the "
                            "current warehouse."
                        )
                    )

    @api.constrains("lot_remove_picking_type_id", "lot_remove_enabled")
    def _check_lot_remove_picking_type(self):
        """Ensure that the picking type for expired lot moves is set when
        expired lot move is enabled."""
        for record in self:
            if record.lot_remove_enabled and not record.lot_remove_picking_type_id:
                raise ValidationError(
                    _("Please set the picking type for expired lot moves.")
                )

    def _get_picking_type_create_values(self, max_sequence):
        """Override to set the picking type for expired lot moves."""
        create_data, max_sequence = super()._get_picking_type_create_values(
            max_sequence
        )
        max_sequence += 1
        create_data["lot_remove_picking_type_id"] = {
            "name": _("Expired Lot Removal"),
            "code": "internal",
            "use_create_lots": False,
            "use_existing_lots": True,
            "default_location_src_id": self.lot_stock_id.id,
            "default_location_dest_id": self.wh_qc_stock_loc_id.id,
            "sequence": max_sequence,
            "sequence_code": "EXP",
            "company_id": self.company_id.id,
            "disable_unassign_lots_to_remove": True,
        }
        return create_data, max_sequence

    def _get_sequence_values(self, name=False, code=False):
        values = super(StockWarehouse, self)._get_sequence_values(name=name, code=code)
        count = self.env["ir.sequence"].search_count(
            [("prefix", "like", self.code + "/EXP%/%")]
        )
        values.update(
            {
                "lot_remove_picking_type_id": {
                    "name": self.name + " " + _("Sequence Expired Lot Removal"),
                    "prefix": self.code
                    + "/"
                    + (
                        self.lot_remove_picking_type_id.sequence_code
                        or (("EXP" + str(count)) if count else "EXP")
                    )
                    + "/",
                    "padding": 5,
                    "company_id": self.company_id.id,
                },
            }
        )
        return values

    @api.model
    def _cron_remove_expired_lots(self):
        """Cron job to remove expired lots."""
        warehouses = self.env["stock.warehouse"].search(
            [("lot_remove_enabled", "=", True)]
        )
        for warehouse in warehouses:
            wizard = self.env["stock.lot.removal.wizard"].create(
                {
                    "warehouse_id": warehouse.id,
                }
            )
            wizard.action_run()
