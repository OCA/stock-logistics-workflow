# Copyright 2026 arielbarreiros96 (https://github.com/arielbarreiros96)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.stock_picking_portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    @http.route(
        ["/my/stock_operations/<int:operation_id>/return"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_stock_operation_return(
        self, operation_id, access_token=None, download=False, **kw
    ):
        """Render the return slip of a delivered stock operation."""
        try:
            operation_sudo = self._document_check_access(
                "stock.picking", operation_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        if not (
            operation_sudo.picking_type_id.portal_visible
            and operation_sudo._portal_is_returnable()
        ):
            raise Forbidden(
                self.env._("You don't have the access rights to Stock Operations.")
            )
        return self._show_report(
            model=operation_sudo,
            report_type="pdf",
            report_ref="stock.return_label_report",
            download=download,
        )
