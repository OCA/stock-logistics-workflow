# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    estimated_landed_cost_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Estimated Landed Cost Product",
        domain=[("landed_cost_ok", "=", True)],
        check_company=True,
        help="Landed-cost service product used for the cost line of the "
        "automatically created estimated landed costs. When set, the "
        "estimate posts a debit on the goods' stock valuation account and "
        "a credit on this product's expense account (e.g. a freight "
        "account), so the actual freight invoice later debits the same "
        "account and its balance becomes the estimate-vs-actual variance. "
        "When empty, each estimate line keeps the purchased product and "
        "both legs of the entry hit the stock valuation account.",
    )
