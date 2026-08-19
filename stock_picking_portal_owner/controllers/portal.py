# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.stock_picking_portal.controllers.portal import (
    CustomerPortal as StockPickingPortal,
)


class StockPickingPortalOwner(StockPickingPortal):
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

    def _prepare_stock_operations_portal_owner_rendering_values(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        filterby=None,
        **kwargs,
    ):
        """
        Prepares the value required for rendering the stock operations
        portal view, including the domain for searching stock picking,
        the sorting order, and the search bar filters and sorting.

        Args:
            page (int, optional): The current page number. Defaults to 1.
            date_begin (str, optional): The start date for filtering stock pickings.
                Defaults to None.
            date_end (str, optional): The end date for filtering stock pickings.
                Defaults to None.
            sortby (str, optional): The field to sort the stock pickings by.
                Defaults to "date".
            filterby (str, optional): The filter to apply to the stock pickings.
                Defaults to "all".
            **kwargs: Additional keyword arguments.

        Returns:
            dict: A dictionary of values to be used for rendering the stock
                operations portal view.
        """
        partner = request.env.user.partner_id
        StockPicking = request.env["stock.picking"]
        url = "/my/stock_operations/owner"
        domain = self._get_prepared_owner_operation_domain(partner)
        if not sortby:
            sortby = "date"
        if not filterby:
            filterby = "all"
        searchbar_filters = self._get_stock_operations_searchbar_filters()
        domain += searchbar_filters[filterby]["domain"]
        values = self._prepare_portal_layout_values()
        searchbar_sortings = self._get_stock_operations_searchbar_sortings()
        sort_order = searchbar_sortings[sortby]["order"]
        if date_begin and date_end:
            domain += [
                ("scheduled_date", ">", date_begin),
                ("scheduled_date", "<=", date_end),
            ]
        pager_values = portal_pager(
            url=url,
            total=StockPicking.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
        )
        operations = StockPicking.search(
            domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager_values["offset"],
        )
        for item in operations:
            item._portal_ensure_token()
        values.update(
            {
                "date": date_begin,
                "stock_operation_ids": operations,
                "pager": pager_values,
                "default_url": url,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
                "searchbar_filters": searchbar_filters,
                "page_name": "owner_stock_operations",
            }
        )
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
        values = self._prepare_stock_operations_portal_owner_rendering_values(**kwargs)
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
