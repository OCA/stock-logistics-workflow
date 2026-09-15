# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class CustomerPortal(portal.CustomerPortal):
    def _get_prepared_move_line_domain(self, partner):
        """Returns a domain to search for stock movements for the given partner.

        Movements are searched on stock.move.line so that every individual
        product movement (incoming or outgoing) linked to the partner's
        pickings can be listed, instead of only the pickings themselves.

        Args:
            partner (res.partner): partner to search movements for.

        Returns:
            list: domain to search for movements for the given partner.

        """
        return [("picking_partner_id", "=", partner.id)]

    def _prepare_home_portal_values(self, counters):
        """
        Values for /my & /my/home routes template rendering.

        Includes the record count for the displayed badges.
        where 'counters' is the list of the displayed badges
        and so the list to compute.
        """
        values = super()._prepare_home_portal_values(counters)
        if "move_operations_count" in counters:
            partner = request.env.user.partner_id
            domain = self._get_prepared_move_line_domain(partner)
            move_operations_count = request.env["stock.move.line"].search_count(domain)
            values["move_operations_count"] = (
                move_operations_count if move_operations_count > 0 else "0"
            )
        return values

    @http.route(
        ["/my/move_operations", "/my/move_operations/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_move_operations(self, **kwargs):
        """
        Prepares the values required for rendering the move operations
        portal view using the `_prepare_move_operations_portal_rendering_values`
        method
        """
        values = self._prepare_move_operations_portal_rendering_values(**kwargs)
        move_ids = values["move_operation_ids"].ids
        request.session["my_operation_history"] = list(dict.fromkeys(move_ids))[:100]
        return request.render(
            "stock_move_line_portal.portal_my_move_operations", values
        )

    def _get_move_operations_searchbar_sortings(self):
        return {
            "date": {"label": _("Movement Date"), "order": "date desc"},
            "name": {"label": _("Reference"), "order": "reference"},
            "state": {"label": _("State"), "order": "state"},
        }

    def _get_move_operations_searchbar_filters(self):
        return {
            "all": {
                "label": _("All"),
                "domain": [("picking_code", "in", ("outgoing", "incoming"))],
            },
            "outgoing": {
                "label": _("Delivery"),
                "domain": [("picking_code", "=", "outgoing")],
            },
            "incoming": {
                "label": _("Receipt"),
                "domain": [("picking_code", "=", "incoming")],
            },
        }

    def _prepare_move_operations_portal_rendering_values(
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
        portal view, including the domain for searching stock move lines,
        the sorting order, and the search bar filters and sorting.

        Args:
            page (int, optional): The current page number. Defaults to 1.
            date_begin (str, optional): The start date for filtering stock move lines.
                Defaults to None.
            date_end (str, optional): The end date for filtering stock move lines.
                Defaults to None.
            sortby (str, optional): The field to sort the stock move lines by.
                Defaults to "date".
            filterby (str, optional): The filter to apply to the stock move lines.
                Defaults to "all".
            **kwargs: Additional keyword arguments.

        Returns:
            dict: A dictionary of values to be used for rendering the move
                operations portal view, including the stock move lines,
                pagination, and search/sort options.
        """
        partner = request.env.user.partner_id
        StockMoveLine = request.env["stock.move.line"]
        domain = self._get_prepared_move_line_domain(partner)
        if not sortby:
            sortby = "date"
        if not filterby:
            filterby = "all"
        searchbar_filters = self._get_move_operations_searchbar_filters()
        domain += searchbar_filters[filterby]["domain"]
        values = self._prepare_portal_layout_values()
        searchbar_sortings = self._get_move_operations_searchbar_sortings()
        sort_order = searchbar_sortings[sortby]["order"]
        if date_begin and date_end:
            domain += [
                ("date", ">", date_begin),
                ("date", "<=", date_end),
            ]
        pager_values = portal_pager(
            url="/my/move_operations",
            total=StockMoveLine.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
        )
        operations = StockMoveLine.search(
            domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager_values["offset"],
        )
        values.update(
            {
                "date": date_begin,
                "move_operation_ids": operations,
                "pager": pager_values,
                "default_url": "/my/move_operations",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
                "searchbar_filters": searchbar_filters,
                "page_name": "move_operations",
            }
        )
        return values

    @http.route(
        ["/my/move_operations/<int:operation_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_move_operation_page(
        self,
        operation_id,
        report_type=None,
        access_token=None,
        message=False,
        download=False,
        **kw,
    ):
        """
        Render the stock operation page for a given operation ID.

        Args:
            operation_id (int): The ID of the stock operation to render.
            report_type (str, optional): The type of report to generate for the
            stock operation.
            Can be "html", "pdf", or "text". Defaults to None.
            access_token (str, optional): The access token for the stock operation.
                                          Defaults to None.
            message (bool or str, optional): A message to display on the page.
                                           Defaults to False.
            download (bool, optional): Whether to download the report.
                                        Defaults to False.
            **kw: Additional keyword arguments.
        """
        try:
            operation_sudo = self._document_check_access(
                "stock.move.line", operation_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        values = {
            "move_operation": operation_sudo,
            "res_company": operation_sudo.company_id,
            "page_name": "move_operation_line",
            "report_type": "html",
            "message": message,
        }
        values = self._get_page_view_values(
            operation_sudo, access_token, values, "my_operation_history", False
        )
        return request.render(
            "stock_move_line_portal.move_operation_portal_template", values
        )
