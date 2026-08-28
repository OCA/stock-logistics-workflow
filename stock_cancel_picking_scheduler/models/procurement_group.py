# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _get_cancel_waiting_pickings_domain(self) -> list:
        """
        Returns the domain to cancel waiting pickings that haven't been started
        yet.
        """
        return [
            ("picking_type_id.cancel_waiting_picking_with_scheduler", "=", True),
            ("state", "in", ("waiting", "confirmed", "assigned")),
            ("printed", "=", False),
            ("user_id", "=", False),
        ]

    @api.model
    def _cancel_waiting_pickings(self) -> None:
        pickings = self.env["stock.picking"].search(
            self._get_cancel_waiting_pickings_domain()
        )
        if pickings:
            pickings.action_cancel()

    @api.model
    def _run_scheduler_tasks(self, use_new_cursor=False, company_id=False):
        self._cancel_waiting_pickings()
        # Notify the remaining tasks
        if "scheduler_task_done" in self.env.context:
            task_done = (
                self.env.context.get("scheduler_task_done", {"task_done": 0})[
                    "task_done"
                ]
                + 1
            )
            self.env.context["scheduler_task_done"]["task_done"] = task_done
        else:
            task_done = self._get_scheduler_tasks_to_do()
        if use_new_cursor:
            self.env["ir.cron"]._notify_progress(
                done=task_done, remaining=self._get_scheduler_tasks_to_do() - task_done
            )
            self.env.cr.commit()  # pylint: disable=E8102
        return super()._run_scheduler_tasks(
            use_new_cursor=use_new_cursor, company_id=company_id
        )
