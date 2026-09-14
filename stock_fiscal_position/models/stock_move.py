# Copyright 2026 Ecosoft (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_account_move_vals(
        self,
        credit_account_id,
        debit_account_id,
        journal_id,
        qty,
        description,
        svl_id,
        cost,
    ):
        self.ensure_one()
        move_vals = super()._prepare_account_move_vals(
            credit_account_id,
            debit_account_id,
            journal_id,
            qty,
            description,
            svl_id,
            cost,
        )
        move_vals["fiscal_position_id"] = self.picking_id.fiscal_position_id.id
        return move_vals

    def _get_accounting_data_for_valuation(self):
        """Return the accounts and journal to use to post Journal Entries for
        the real-time valuation of the quant."""
        self.ensure_one()
        journal_id, acc_src, acc_dest, acc_valuation = (
            super()._get_accounting_data_for_valuation()
        )
        fiscal_position = self.picking_id.fiscal_position_id
        if not fiscal_position:
            return journal_id, acc_src, acc_dest, acc_valuation

        account_model = self.env["account.account"]

        if acc_src:
            acc_src = fiscal_position.map_account(account_model.browse(acc_src)).id
        if acc_dest:
            acc_dest = fiscal_position.map_account(account_model.browse(acc_dest)).id
        if acc_valuation:
            acc_valuation = fiscal_position.map_account(
                account_model.browse(acc_valuation)
            ).id
        return journal_id, acc_src, acc_dest, acc_valuation
