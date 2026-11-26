# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from odoo import api, models

from odoo.addons.base_exception.exceptions import BaseExceptionError

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = ["stock.picking", "base.exception"]
    _name = "stock.picking"

    @api.model
    def test_all_draft_pickings(self):
        picking_set = self.search([("state", "=", "draft")])
        try:
            picking_set.detect_exceptions()
        except BaseExceptionError:
            # Exceptions are stored before the rollback: don't fail the cron.
            _logger.info("Exceptions detected on draft pickings")
        return True

    @api.model
    def _reverse_field(self):
        return "picking_ids"

    def detect_exceptions(self):
        all_exceptions = super().detect_exceptions()
        moves = self.mapped("move_ids")
        all_exceptions += moves.detect_exceptions()
        return all_exceptions

    @api.constrains("ignore_exception", "move_ids", "state")
    def stock_check_exception(self):
        pickings = self.filtered(
            lambda s: s.state in ["waiting", "confirmed", "assigned"]
        )
        if pickings:
            # Only the ids are needed here: keep the ValidationError.
            pickings.with_context(
                base_exception_no_rollback={pickings._name: pickings.ids}
            )._check_exception()

    @api.onchange("move_ids")
    def onchange_ignore_exception(self):
        if self.state in ["waiting", "confirmed", "assigned"]:
            self.ignore_exception = False

    def _must_popup_exception(self):
        return True

    def action_confirm(self):
        self.detect_exceptions()
        return super().action_confirm()

    def button_validate(self):
        self.detect_exceptions()
        return super().button_validate()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref("stock_exception.action_stock_exception_confirm")
        return action
