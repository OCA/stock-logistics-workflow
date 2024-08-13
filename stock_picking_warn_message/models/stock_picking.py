# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.base.models.res_partner import WARNING_HELP, WARNING_MESSAGE


class StockPicking(models.Model):
    _inherit = "stock.picking"

    picking_warn = fields.Selection(
        selection=WARNING_MESSAGE, compute="_compute_picking_warn", help=WARNING_HELP
    )
    picking_warn_msg = fields.Text(compute="_compute_picking_warn_msg")

    @api.depends(
        "state",
        "partner_id.picking_warn",
        "partner_id.commercial_partner_id.picking_warn",
    )
    def _compute_picking_warn(self):
        for rec in self:
            picking_warn = "no-message"
            if rec.state not in ["done", "cancel"] and rec.partner_id:
                p = rec.partner_id.commercial_partner_id
                if p.picking_warn == "block" or rec.partner_id.picking_warn == "block":
                    picking_warn = "block"
                elif (
                    p.picking_warn == "warning"
                    or rec.partner_id.picking_warn == "warning"
                ):
                    picking_warn = "warning"
            rec.picking_warn = picking_warn

    @api.depends(
        "state",
        "partner_id.picking_warn",
        "partner_id.commercial_partner_id.picking_warn",
    )
    def _compute_picking_warn_msg(self):
        for rec in self:
            picking_warn_msg = ""
            if rec.state not in ["done", "cancel"] and rec.partner_id:
                p = rec.partner_id.commercial_partner_id
                separator = ""
                if p.picking_warn != "no-message":
                    separator = "\n"
                    picking_warn_msg += p.picking_warn_msg
                if p != rec.partner_id and rec.partner_id.picking_warn != "no-message":
                    picking_warn_msg += separator + rec.partner_id.picking_warn_msg
            rec.picking_warn_msg = picking_warn_msg or False
