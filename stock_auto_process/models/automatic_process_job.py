# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class AutomaticProcessJob(models.AbstractModel):
    _name = "automatic.process.job"
    _description = "Stock Automatic Process Job"

    @api.model
    def run(self):
        """Entry point for the scheduled action."""
        rules = self.env["stock.auto.process.rule"].search([])
        for rule in rules:
            try:
                with self.env.cr.savepoint():
                    self._process_rule(rule)
            except Exception as e:  # noqa: BLE001
                _logger.warning(
                    "Auto-process rule %s aborted: %s",
                    rule.display_name,
                    e,
                )

    def _process_rule(self, rule):
        for picking in rule._search_pickings():
            self._process_picking(rule, picking)

    def _process_picking(self, rule, picking):
        try:
            with self.env.cr.savepoint():
                self._apply_actions(rule, picking)
                if picking.state == "done":
                    picking.message_post(
                        body=_("Auto-processed by rule %s.") % rule.display_name
                    )
        except Exception as e:  # noqa: BLE001
            _logger.warning(
                "Auto-process rule %s failed on picking %s: %s",
                rule.display_name,
                picking.display_name,
                e,
            )

    def _apply_actions(self, rule, picking):
        if rule.do_confirm and picking.state == "draft":
            picking.action_confirm()
        if rule.do_assign and picking.state in ("confirmed", "partially_available"):
            picking.action_assign()
        if rule.do_validate and picking.state in ("assigned", "partially_available"):
            self._auto_validate(rule, picking)

    def _auto_validate(self, rule, picking):
        """Validate ``picking`` server-side, bypassing the immediate-transfer
        and backorder confirmation wizards.

        Mirrors what those wizards do internally:
        - fills ``qty_done`` from the reservation on moves where it is zero
          (what ``stock.immediate.transfer.process`` does);
        - calls ``button_validate`` with ``skip_immediate`` / ``skip_backorder``
          so no wizard action is returned, and passes
          ``picking_ids_not_to_backorder`` when the rule should not create
          a backorder.
        """
        picking.action_set_quantities_to_reservation()
        ctx = {"skip_immediate": True, "skip_backorder": True}
        if not rule.create_backorder:
            ctx["picking_ids_not_to_backorder"] = picking.ids
        picking.with_context(**ctx).button_validate()
