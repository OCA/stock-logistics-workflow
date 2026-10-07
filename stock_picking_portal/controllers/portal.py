# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import binascii

from odoo import _, fields, http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request

from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class CustomerPortal(portal.CustomerPortal):
    def _get_prepared_operation_domain(self, partner):
        visible_ids = request.env["stock.picking"].sudo()._get_available_operations()
        visible_ids = visible_ids or [-1]
        return [
            ("partner_id", "=", partner.id),
            ("picking_type_id", "in", visible_ids),
        ]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "stock_operations_count" in counters:
            partner = request.env.user.partner_id
            domain = self._get_prepared_operation_domain(partner)
            count_ = request.env["stock.picking"].sudo().search_count(domain)
            values["stock_operations_count"] = count_ if count_ > 0 else "0"
        return values

    @http.route(
        ["/my/stock_operations", "/my/stock_operations/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_stock_operations(self, **kwargs):
        values = self._prepare_stock_operations_portal_rendering_values(**kwargs)
        history = values["stock_operation_ids"].ids[:100]
        request.session["my_operation_history"] = history
        return request.render("stock_picking_portal.portal_my_stock_operations", values)

    def _get_stock_operations_searchbar_sortings(self):
        return {
            "date": {"label": _("Order Date"), "order": "scheduled_date desc"},
            "name": {"label": _("Reference"), "order": "name"},
            "state": {"label": _("State"), "order": "state"},
        }

    def _get_stock_operations_searchbar_filters(self):
        return {
            "all": {
                "label": _("All"),
                "domain": [("picking_type_id.code", "in", ("outgoing", "incoming"))],
            },
            "outgoing": {
                "label": _("Delivery"),
                "domain": [("picking_type_id.code", "=", "outgoing")],
            },
            "incoming": {
                "label": _("Receipt"),
                "domain": [("picking_type_id.code", "=", "incoming")],
            },
        }

    def _prepare_stock_operations_portal_rendering_values(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        filterby=None,
        **kwargs,
    ):
        partner = request.env.user.partner_id
        StockPicking = request.env["stock.picking"].sudo()
        url = "/my/stock_operations"

        domain = self._get_prepared_operation_domain(partner)

        sortby = sortby or "date"
        filterby = filterby or "all"

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
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
                "filterby": filterby,
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
                "date": date_begin,
                "stock_operation_ids": operations,
                "pager": pager_values,
                "default_url": url,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
                "searchbar_filters": searchbar_filters,
                "filterby": filterby,
                "page_name": "stock_operations",
            }
        )
        return values

    @http.route(
        ["/my/stock_operations/<int:operation_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_stock_operation_page(
        self,
        operation_id,
        report_type=None,
        access_token=None,
        message=False,
        download=False,
        **kw,
    ):
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

        visible_ids = request.env["stock.picking"].sudo()._get_available_operations()
        if not visible_ids or operation_sudo.picking_type_id.id not in visible_ids:
            return request.make_response(
                _("Operation not available in portal."),
                headers=[("Content-Type", "text/plain; charset=utf-8")],
                status=403,
            )

        if request.env.user.share and access_token:
            today = fields.Date.today().isoformat()
            session_key = f"view_stock_operation_{operation_sudo.id}"
            session_obj_date = request.session.get(session_key)
            if session_obj_date != today:
                request.session[session_key] = today
                viewer = (
                    operation_sudo.partner_id.name
                    if request.env.user._is_public()
                    else request.env.user.partner_id.name
                )
                msg = _("Stock Operation viewed by customer %s") % viewer
                operation_sudo.message_post(
                    body=msg,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=operation_sudo.user_id.sudo().partner_id.ids,
                )

        values = {
            "stock_operations": operation_sudo,
            "res_company": operation_sudo.company_id,
            "page_name": "stock_operations",
            "report_type": "html",
            "message": message,
        }
        values = self._get_page_view_values(
            operation_sudo, access_token, values, "my_operation_history", False
        )
        return request.render(
            "stock_picking_portal.stock_operation_portal_template", values
        )

    @http.route(
        ["/my/stock_operations/<int:operation_id>/accept"],
        type="json",
        auth="public",
        website=True,
    )
    def portal_stock_operations_accept(
        self, operation_id, access_token=None, name=None, signature=None
    ):
        access_token = access_token or request.httprequest.args.get("access_token")
        try:
            operation_sudo = self._document_check_access(
                "stock.picking", operation_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return {"error": _("Invalid Stock Operation.")}

        if not signature:
            return {"error": _("Signature is missing.")}

        try:
            operation_sudo.write(
                {
                    "signed_by": name,
                    "signed_on": fields.Datetime.now(),
                    "signature": signature,
                }
            )
        except (TypeError, binascii.Error, UserError):
            return {"error": _("Invalid signature data.")}

        pdf = (
            request.env["ir.actions.report"]
            .sudo()
            ._render_qweb_pdf("stock.action_report_delivery", [operation_sudo.id])[0]
        )

        body = _("Stock Operation signed by %s") % name
        operation_sudo.message_post(
            body=body,
            attachments=[(f"{operation_sudo.name}.pdf", pdf)],
        )

        query_string = "&message=sign_ok"
        return {
            "force_refresh": True,
            "redirect_url": operation_sudo.get_portal_url(query_string=query_string),
        }
