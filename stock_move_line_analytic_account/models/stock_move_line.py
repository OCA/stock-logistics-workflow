from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        compute="_compute_analytic_account_id",
        store=True,
        index=True,
        readonly=True,
    )

    @api.depends("move_id.analytic_distribution")
    def _compute_analytic_account_id(self):
        AnalyticAccount = self.env["account.analytic.account"]
        for line in self:
            distribution = line.move_id.analytic_distribution or {}
            account = AnalyticAccount
            # Sort by percentage descending, pick first valid account
            for aid in sorted(distribution, key=distribution.get, reverse=True):
                account = AnalyticAccount.browse(int(aid)).exists()
                if account:
                    break
            line.analytic_account_id = account
