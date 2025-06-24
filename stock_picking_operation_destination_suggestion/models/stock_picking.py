# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.osv.expression import AND


class StockPicking(models.Model):

    _inherit = "stock.picking"

    destination_location_suggestion_ids = fields.Many2many(
        comodel_name="stock.location",
        string="Suggested Destination Locations",
        compute="_compute_destination_location_suggestion_ids",
    )
    suggest_destination_visible = fields.Boolean(
        compute="_compute_suggest_destination_visible",
    )

    @api.depends("state", "picking_type_id.suggest_destination")
    def _compute_suggest_destination_visible(self):
        for picking in self:
            picking.suggest_destination_visible = bool(
                picking.state == "assigned"
                and picking.picking_type_id.suggest_destination
            )

    def _get_location_destination_move_line_suggestion_domain(self):
        domain = self.picking_type_id.suggest_destination_additional_domain
        if self.picking_type_id.suggest_destination_partner:
            domain = AND(
                [
                    domain,
                    [("picking_id.partner_id", "in", self.partner_id.ids)],
                ]
            )
        return domain

    @api.depends(
        "partner_id", "location_dest_id.children_ids.pending_out_move_line_ids"
    )
    def _compute_destination_location_suggestion_ids(self):
        for picking in self:
            pending_line_ids = (
                picking.location_dest_id.children_ids.pending_out_move_line_ids
            )
            domain = self._get_location_destination_move_line_suggestion_domain()
            locations = (
                pending_line_ids.filtered_domain(domain).location_id
                if picking.picking_type_id.suggest_destination
                else self.env["stock.location"].browse()
            )
            picking.destination_location_suggestion_ids = locations

    def suggest_destination(self):
        """
        Launch the destination suggestion wizard
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_picking_operation_destination_suggestion."
            "stock_picking_operation_destination_suggest_act_window"
        )
        return action
