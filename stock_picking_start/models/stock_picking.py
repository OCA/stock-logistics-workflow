# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):

    _inherit = "stock.picking"

    user_id = fields.Many2one(
        "res.users",
        default=lambda self: self._default_user_id,
    )
    action_start_allowed = fields.Boolean(
        compute="_compute_action_start_allowed",
    )
    action_cancel_start_allowed = fields.Boolean(
        compute="_compute_action_cancel_start_allowed"
    )

    started = fields.Boolean(
        compute="_compute_started",
        inverse="_inverse_started",
        store=True,
    )

    def _default_user_id(self):
        if not self.env.company.stock_picking_assign_operator_at_start:
            return self.env.user
        return False

    @api.depends("state", "printed")
    def _compute_action_start_allowed(self):
        for record in self:
            record.action_start_allowed = (
                record.state == "assigned" and not record.printed
            )

    @api.depends("state", "printed")
    def _compute_action_cancel_start_allowed(self):
        for record in self:
            record.action_cancel_start_allowed = (
                record.state == "assigned" and record.printed
            )

    @api.depends("printed", "state")
    def _compute_started(self):
        for record in self:
            record.started = record.state == "assigned" and record.printed

    def _inverse_started(self):
        for record in self:
            if record.started:
                record._check_action_start_allowed()
                vals = record._prepare_start_values(record.company_id)
            else:
                record._check_action_cancel_start_allowed()
                vals = record._prepare_cancel_start_values(record.company_id)
            record.write(vals)

    def _check_action_start_allowed(self):
        no_start_allowed = self.filtered(lambda p: not p.action_start_allowed)
        if no_start_allowed:
            raise UserError(
                _(
                    "The following picking(s) can't be started:\n" "%(names)s",
                    names="\n".join(no_start_allowed.mapped("name")),
                )
            )

    def _check_action_cancel_start_allowed(self):
        no_reset_allowed = self.filtered(lambda p: not p.action_cancel_start_allowed)
        if no_reset_allowed:
            raise UserError(
                _(
                    "The 'started' status of the following picking(s) can't be "
                    "cancelled:\n"
                    "%(names)s",
                    names="\n".join(no_reset_allowed.mapped("name")),
                )
            )

    def _prepare_start_values(self, company):
        self.ensure_one()
        value = {"printed": True}
        if company.stock_picking_assign_operator_at_start:
            value["user_id"] = self.env.uid
        return value

    def _prepare_cancel_start_values(self, company):
        self.ensure_one()
        value = {"printed": False}
        if company.stock_picking_assign_operator_at_start:
            value["user_id"] = False
        return value

    def action_start(self):
        self._check_action_start_allowed()
        self.write({"started": True})

    def action_cancel_start(self):
        self._check_action_cancel_start_allowed()
        self.write({"started": False})
