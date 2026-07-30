import json

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
            distribution = line.move_id.analytic_distribution
            if distribution:
                if isinstance(distribution, str):
                    distribution = json.loads(distribution)
                if distribution:
                    # Sort by percentage descending, pick first valid account
                    sorted_ids = sorted(
                        distribution, key=distribution.get, reverse=True
                    )
                    account = AnalyticAccount
                    for aid in sorted_ids:
                        account = AnalyticAccount.browse(int(aid)).exists()
                        if account:
                            break
                    line.analytic_account_id = account or False
                else:
                    line.analytic_account_id = False
            else:
                line.analytic_account_id = False
