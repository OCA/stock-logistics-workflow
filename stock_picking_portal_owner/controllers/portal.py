# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.stock_picking_portal.controllers.portal import (
    CustomerPortal as StockPickingPortal,
)


class CustomerPortal(StockPickingPortal):
    def _get_prepared_owner_operation_domain(self, partner):
        portal_visible_operation_ids = (
            request.env["stock.picking.type"].sudo()._get_available_operations()
        )
        return [
            ("owner_id", "=", partner.id),
            ("picking_type_id", "in", portal_visible_operation_ids),
        ]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "owner_stock_operations_count" in counters:
            domain = self._get_prepared_owner_operation_domain(
                request.env.user.partner_id
            )
            values["owner_stock_operations_count"] = request.env[
                "stock.picking"
            ].search_count(domain)
        return values

    def _get_stock_operations_base_url(self):
        return "/my/stock_operations/owner"

    def _prepare_owner_stock_operations_portal_rendering_values(self, **kwargs):
        domain = self._get_prepared_owner_operation_domain(request.env.user.partner_id)
        values = super()._prepare_stock_operations_portal_rendering_values(
            domain=domain,
            base_url=self._get_stock_operations_base_url(),
            **kwargs,
        )
        values["page_name"] = "owner_stock_operations"
        return values

    @http.route(
        [
            "/my/stock_operations/owner",
            "/my/stock_operations/owner/page/<int:page>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_owner_stock_operations(self, **kwargs):
        values = self._prepare_owner_stock_operations_portal_rendering_values(**kwargs)
        request.session["my_owner_operation_history"] = values[
            "stock_operation_ids"
        ].ids[:100]
        return request.render("stock_picking_portal.portal_my_stock_operations", values)

    @http.route(
        ["/my/stock_operations/owner/<int:operation_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_owner_stock_operation_page(self, operation_id, **kwargs):
        domain = [
            ("id", "=", operation_id)
        ] + self._get_prepared_owner_operation_domain(request.env.user.partner_id)
        operation = request.env["stock.picking"].search(domain, limit=1)
        if not operation:
            return request.redirect("/my")
        request.session["my_operation_history"] = request.session.get(
            "my_owner_operation_history", []
        )
        return super().portal_stock_operation_page(operation_id, **kwargs)
