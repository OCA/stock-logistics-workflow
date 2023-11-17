from odoo import _, api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    inter_warehouse_route_id = fields.Many2one(
        "stock.location.route",
        ondelete="restrict",
        check_company=True,
        help="The route to use for inter warehouse transfers",
    )

    def _create_per_company_routes(self):
        if hasattr(super(), "_create_per_company_routes"):
            super()._create_per_company_routes()
        iw_route = self.env["stock.location.route"].create(
            {
                "name": self.name + ": " + _("Inter-Warehouse"),
                "product_selectable": False,
                "product_categ_selectable": False,
                "warehouse_selectable": True,
                "company_id": self.id,
            }
        )
        self.inter_warehouse_route_id = iw_route

    @api.model
    def create_missing_route(self):
        """This hook is used to add an inter-warehouse route
        on existing companies when module is installed.
        """
        company_ids = (
            self.env["res.company"]
            .with_context(active_test=False)
            .search([("inter_warehouse_route_id", "=", False)])
        )
        for company in company_ids:
            company.sudo()._create_per_company_routes()

    @api.model
    def create(self, vals):
        company = super(Company, self).create(vals)
        company.sudo()._create_per_company_routes()
        return company
