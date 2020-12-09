# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from itertools import groupby

from odoo import _, api, exceptions, fields
from odoo.models import TransientModel
from odoo.tools import DotDict


class StockPickingMergeWizard(TransientModel):
    _name = "stock.picking.merge"
    _description = "Stock Picking Merge"

    selected_picking_ids = fields.Many2many(
        string="Selected Pickings",
        comodel_name="stock.picking",
        default=lambda self: self.env.context.get("active_ids"),
    )
    valid_picking_ids = fields.Many2many(
        string="Valid Pickings",
        comodel_name="stock.picking",
        compute="_compute_pickings",
    )
    discarded_picking_ids = fields.Many2many(
        string="Discarded Pickings",
        comodel_name="stock.picking",
        compute="_compute_pickings",
    )
    details = fields.Html(compute="_compute_info")
    nothing_todo = fields.Boolean(compute="_compute_info")
    show_discarded_detail = fields.Boolean(default=False)

    @api.depends("selected_picking_ids")
    def _compute_pickings(self):
        for rec in self:
            valid_pickings = rec._valid_pickings()
            discarded = rec.selected_picking_ids - valid_pickings
            rec.update(
                {
                    "discarded_picking_ids": discarded.ids,
                    "valid_picking_ids": valid_pickings.ids,
                }
            )

    def _valid_pickings(self):
        return self.selected_picking_ids.filtered(self._filter_picking).sorted(
            key=self._key_group_picking,
        )

    @staticmethod
    def _filter_picking(picking):
        return (
            picking.picking_type_id.group_pickings
            and picking.state not in ("cancel", "done")
            and not picking.printed
        )

    @staticmethod
    def _key_group_picking(picking):
        return (
            picking.partner_id.id or 0,
            picking.carrier_id.id or 0,
            picking.location_id.id,
            picking.location_dest_id.id,
            picking.picking_type_id.id,
        )

    def _grouped_pickings(self):
        return groupby(self.valid_picking_ids, key=self._key_group_picking)

    @api.depends("valid_picking_ids")
    def _compute_info(self):
        tmpl = self._get_info_template()
        for rec in self:
            info = rec._get_grouping_info()
            rec.details = tmpl.render(info)
            rec.nothing_todo = not info["something_todo"]

    def _get_grouping_info(self):
        grouping_forecast = []
        for key, _pickings in self._grouped_pickings():
            partner = self.env["res.partner"].browse()
            carrier = self.env["delivery.carrier"].browse()
            partner_id, carrier_id = key[:2]
            if partner_id:
                partner = partner.browse(partner_id)
            if carrier_id:
                carrier = carrier.browse(carrier_id)

            pickings = tuple(_pickings)
            grouping_forecast.append(
                DotDict(
                    {
                        "partner": partner,
                        "carrier": carrier,
                        "pickings": pickings,
                        "has_todo": len(pickings) > 1,
                    }
                )
            )
        discarded = self.discarded_picking_ids
        return {
            "grouping_forecast": grouping_forecast,
            "discarded_pickings": discarded,
            "something_todo": any([x["has_todo"] for x in grouping_forecast]),
        }

    def _get_info_template(self):
        mod = "stock_picking_group_by_partner_by_carrier"
        return self.env.ref(mod + ".stock_picking_merge_wiz_info")

    def action_merge(self):
        self.ensure_one()
        if self.nothing_todo:
            raise exceptions.UserError(_("No picking can be merged!"))
        # Make sure valid pickings are still valid
        self._compute_pickings()
        moves = self.valid_picking_ids.mapped("move_lines")
        moves.write({"picking_id": False})
        moves.with_context(picking_manual_merge=True)._assign_picking()
        # Cancel old pickings left w/out moves if needed
        self.valid_picking_ids._check_emptyness_after_merge()
        return {
            "name": _("Grouped pickings"),
            "domain": [("id", "in", moves.mapped("picking_id").ids)],
            "res_model": "stock.picking",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "tree,form",
            "context": self.env.context,
        }
