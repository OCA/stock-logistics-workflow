# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, http
from odoo.http import request

from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager

MOVE_STATES = {
    "draft": _("New"),
    "waiting": _("Waiting Another Move"),
    "confirmed": _("Waiting Availability"),
    "partially_available": _("Partially Available"),
    "assigned": _("Available"),
    "done": _("Done"),
    "cancel": _("Cancelled"),
}


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
        return [("owner_id", "=", partner.id)]

    def _prepare_home_portal_values(self, counters):
        """
        Values for /my & /my/home routes template rendering.

        Includes the record count for the displayed badges.
        where 'counters' is the list of the displayed badges
        and so the list to compute.
        """
        values = super()._prepare_home_portal_values(counters)
        if "stock_move_line_owner_count" in counters:
            partner = request.env.user.partner_id
            domain = self._get_prepared_move_line_domain(partner)
            stock_move_line_owner_count = request.env["stock.move.line"].search_count(
                domain
            )
            values["stock_move_line_owner_count"] = (
                stock_move_line_owner_count if stock_move_line_owner_count > 0 else "0"
            )
        return values

    @http.route(
        ["/my/stock_move_line/owner", "/my/stock_move_line/owner/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_stock_move_line_owner(self, **kwargs):
        """
        Prepares the values required for rendering the move operations
        portal view using the `_prepare_stock_move_line_owner_portal_rendering_values`
        method
        """
        values = self._prepare_stock_move_line_owner_portal_rendering_values(**kwargs)
        move_ids = values["move_operation_ids"].ids
        request.session["my_operation_history"] = move_ids[:100]
        return request.render(
            "stock_move_line_portal_owner.portal_my_stock_move_line_owner", values
        )

    def _get_stock_move_line_owner_searchbar_sortings(self):
        return {
            "date": {"label": _("Movement Date"), "order": "date desc"},
            "name": {"label": _("Reference"), "order": "reference"},
            "state": {"label": _("State"), "order": "state"},
        }

    def _get_stock_move_line_owner_searchbar_filters(self):
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

    def _prepare_stock_move_line_owner_portal_rendering_values(
        self,
        page=1,
        date_from=None,
        date_to=None,
        move_state=None,
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
            date_from (str, optional): The start date for filtering stock move lines.
                Defaults to None.
            date_to (str, optional): The end date for filtering stock move lines.
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
        StockMoveLine = request.env["stock.move.line"].sudo()
        domain = self._get_prepared_move_line_domain(partner)
        if not sortby:
            sortby = "date"
        if not filterby:
            filterby = "all"
        searchbar_filters = self._get_stock_move_line_owner_searchbar_filters()
        domain += searchbar_filters[filterby]["domain"]
        values = self._prepare_portal_layout_values()
        searchbar_sortings = self._get_stock_move_line_owner_searchbar_sortings()
        sort_order = searchbar_sortings[sortby]["order"]
        if date_from and date_to:
            domain += [
                ("date", ">", date_from),
                ("date", "<=", date_to),
            ]
        if move_state and move_state != "all":
            domain += [("state", "=", move_state)]
        pager_values = portal_pager(
            url="/my/stock_move_line/owner",
            total=StockMoveLine.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={
                "date_from": date_from,
                "date_to": date_to,
                "sortby": sortby,
                "move_state": move_state,
            },
        )
        operations = StockMoveLine.search(
            domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager_values["offset"],
        )
        values.update(
            {
                "date_from": date_from,
                "date_to": date_to,
                "move_operation_ids": operations,
                "pager": pager_values,
                "default_url": "/my/stock_move_line/owner",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
                "searchbar_filters": searchbar_filters,
                "page_name": "stock_move_line_owner",
                "move_states": MOVE_STATES,
                "move_state": move_state,
            }
        )
        return values
