# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, http
from odoo.exceptions import AccessDenied, AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.stock_picking_portal.controllers.portal import (
    CustomerPortal as StockPickingPortal,
)

MOVE_STATES = {
    "draft": _("New"),
    "waiting": _("Waiting Another Move"),
    "confirmed": _("Waiting Availability"),
    "partially_available": _("Partially Available"),
    "assigned": _("Available"),
    "done": _("Done"),
    "cancel": _("Cancelled"),
}


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
            owner_stock_operations_count = request.env["stock.picking"].search_count(
                domain
            )
            values["owner_stock_operations_count"] = (
                owner_stock_operations_count and owner_stock_operations_count or "0"
            )
        return values

    def _prepare_stock_operations_portal_owner_rendering_values(
        self,
        page=1,
        date_from=None,
        date_to=None,
        sortby=None,
        filterby=None,
        move_state=None,
        **kwargs,
    ):
        """
        Prepares the value required for rendering the stock operations
        portal view, including the domain for searching stock picking,
        the sorting order, and the search bar filters and sorting.

        Args:
            page (int, optional): The current page number. Defaults to 1.
            date_from (str, optional): The start date for filtering stock pickings.
                Defaults to None.
            date_to (str, optional): The end date for filtering stock pickings.
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
        values = self._prepare_portal_layout_values()
        searchbar_sortings = self._get_stock_operations_searchbar_sortings()
        sort_order = searchbar_sortings[sortby]["order"]
        if date_from and date_to:
            domain += [
                ("scheduled_date", ">", date_from),
                ("scheduled_date", "<", date_to),
            ]
        if move_state and move_state != "all":
            domain += [("state", "=", move_state)]
        pager_values = portal_pager(
            url=url,
            total=StockPicking.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={
                "date_from": date_from,
                "date_to": date_to,
                "sortby": sortby,
                "move_state": move_state,
            },
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
                "date_to": date_to,
                "date_from": date_from,
                "stock_operation_ids": operations,
                "pager": pager_values,
                "default_url": url,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
                "searchbar_filters": {},
                "page_name": "owner_stock_operations",
                "move_states": MOVE_STATES,
                "move_state": move_state,
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
        auth="public",
        website=True,
    )
    def portal_owner_stock_operation_page(
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
                "stock.picking", operation_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        if report_type in ("html", "pdf", "text"):
            return self._show_report(
                model=operation_sudo,
                report_type=report_type,
                report_ref="stock.action_report_delivery",
                download=download,
            )
        portal_visible_operation_ids = (
            request.env["stock.picking.type"].sudo()._get_available_operations()
        )
        if (
            not portal_visible_operation_ids
            or operation_sudo.picking_type_id.id not in portal_visible_operation_ids
        ):
            raise AccessDenied(
                _("You don't have the access rights to Stock Operations.")
            )
        if request.env.user.share and access_token:
            today = fields.Date.today().isoformat()
            session_obj_date = request.session.get(
                "view_stock_operation_%s" % operation_sudo.id
            )
            if session_obj_date != today:
                request.session["view_stock_operation_%s" % operation_sudo.id] = today
                msg = _(
                    "Stock Operation viewed by customer %s",
                    (
                        operation_sudo.partner_id.name
                        if request.env.user._is_public()
                        else request.env.user.partner_id.name
                    ),
                )
                _message_post_helper(
                    "stock.picking",
                    operation_sudo.id,
                    message=msg,
                    token=operation_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=operation_sudo.user_id.sudo().partner_id.ids,
                )
        values = {
            "owner_stock_operations": operation_sudo,
            "res_company": operation_sudo.company_id,
            "page_name": "owner_stock_operations",
            "report_type": "html",
            "message": message,
        }
        values = self._get_page_view_values(
            operation_sudo, access_token, values, "my_owner_operation_history", False
        )
        return request.render(
            "stock_picking_portal.stock_operation_portal_template", values
        )
