# Copyright 2017 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command, _, api, fields, models


class StockBackorderReasonChoice(models.TransientModel):
    _name = "stock.backorder.reason.choice"
    _description = "Stock Backorder Reason Choice"

    reason_id = fields.Many2one(
        comodel_name="stock.backorder.reason",
        string="Backorder reason",
        required=True,
        ondelete="cascade",
    )
    backorder_action_to_do = fields.Selection(
        related="reason_id.backorder_action_to_do",
    )
    picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        relation="stock_picking_backorder_reason_choice_rel",
    )
    choice_line_ids = fields.One2many(
        comodel_name="stock.backorder.reason.choice.line",
        inverse_name="wizard_id",
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if "choice_line_ids" in fields and res.get("picking_ids"):
            res["choice_line_ids"] = [
                Command.create({"picking_id": pick_id})
                for pick_id in res["picking_ids"][0][2]
            ]
        return res

    def _get_message(self):
        self.ensure_one()
        return _("Back order reason: <em>{reason}</em>.").format(
            reason=self.reason_id.name
        )

    def _prepare_backorder_confirmation_line(self, picking):
        return {
            "to_backorder": True,
            "picking_id": picking.id,
        }

    def _prepare_backorder_confirmation(self, pickings):
        """
        Prepare the values to create the backorder confirmation
        """
        self.ensure_one()
        return {
            "backorder_confirmation_line_ids": [
                Command.create(self._prepare_backorder_confirmation_line(picking))
                for picking in pickings
            ]
        }

    def apply(self):
        confirmation_obj = self.env["stock.backorder.confirmation"]
        for wizard in self:
            pickings = wizard.choice_line_ids.mapped("picking_id")
            # Set the reason on each picking
            pickings.message_post(body=wizard._get_message())
            keep_backorder_pickings = self.env["stock.picking"].browse()
            if wizard.backorder_action_to_do == "create":
                keep_backorder_pickings = pickings
            elif wizard.backorder_action_to_do == "use_partner_option":
                keep_backorder_pickings = pickings.filtered(
                    lambda picking: picking.backorder_reason_strategy == "create"
                )
            elif not wizard.backorder_action_to_do:
                # Let do the normal way
                return pickings.with_context(
                    skip_backorder_reason=True
                )._pre_action_done_hook()
            pickings_to_cancel = pickings - keep_backorder_pickings
            if keep_backorder_pickings:
                backorder_wizard = confirmation_obj.create(
                    wizard._prepare_backorder_confirmation(keep_backorder_pickings)
                )
                backorder_wizard.with_context(skip_backorder_reason=True).process()

            if pickings_to_cancel:
                backorder_wizard = confirmation_obj.with_context(
                    default_pick_ids=pickings_to_cancel.ids
                ).create(wizard._prepare_backorder_confirmation(pickings_to_cancel))
                backorder_wizard.with_context(
                    skip_backorder_reason=True
                ).process_cancel_backorder()
        return True
