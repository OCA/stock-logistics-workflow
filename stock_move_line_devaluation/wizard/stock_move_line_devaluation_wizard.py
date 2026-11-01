import datetime as dt
import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockMoveLineDevaluationWizard(models.TransientModel):
    _name = "stock.move.line.devaluation.wizard"
    _description = "Stock Withdrawal Valuation Wizard"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
    )
    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        string="Pricelist",
    )
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.pricelist_id = self.partner_id.property_product_pricelist

    def _get_move_line_domain(self):
        """Build search domain for outgoing done move lines."""
        domain = [
            ("state", "=", "done"),
            ("location_dest_id.usage", "=", "customer"),
        ]
        if self.partner_id:
            domain.append(("picking_id.partner_id", "=", self.partner_id.id))
        if self.date_from:
            date_from_dt = dt.datetime.combine(self.date_from, dt.time.min)
            domain.append(("date", ">=", date_from_dt))
        if self.date_to:
            date_to_dt = dt.datetime.combine(self.date_to, dt.time.max)
            domain.append(("date", "<=", date_to_dt))
        return domain

    def _compute_net_qty(self, move_line):
        """Calculate net quantity considering proportional returns."""
        move = move_line.move_id
        if not move.quantity_done:
            return 0.0
        total_returned = sum(
            rm.quantity_done for rm in move.returned_move_ids if rm.state == "done"
        )
        ratio = move_line.qty_done / move.quantity_done
        returned_for_line = total_returned * ratio
        return move_line.qty_done - returned_for_line

    def _get_unit_price(self, product, quantity, date):
        """Get unit price from pricelist or fallback to list price."""
        pricelist = self.pricelist_id
        if pricelist and product:
            report_date = date.date() if isinstance(date, dt.datetime) else date
            try:
                price = pricelist._get_product_price(
                    product,
                    quantity or 1.0,
                    date=report_date or fields.Date.today(),
                )
                if price:
                    return price
            except Exception as exc:
                _logger.debug("Pricelist price error: %s", exc)
        return product.lst_price if product else 0.0

    def _get_analytic_account_id(self, move_line):
        """Extract the main analytic account from analytic_distribution."""
        move = move_line.move_id
        distribution = getattr(move, "analytic_distribution", None)
        if not distribution:
            return False
        if isinstance(distribution, str):
            distribution = json.loads(distribution)
        if not distribution:
            return False
        account_model = self.env["account.analytic.account"]
        sorted_ids = sorted(distribution, key=distribution.get, reverse=True)
        for aid in sorted_ids:
            account = account_model.browse(int(aid)).exists()
            if account:
                return account.id
        return False

    def _get_responsible_id(self, picking):
        """Get responsible user from picking using sudo for access."""
        if not picking:
            return False
        user = picking.sudo().user_id
        return user.id if user else False

    def _prepare_report_line(self, move_line, net_qty, unit_price):
        """Prepare values dict for a report line."""
        picking = move_line.picking_id
        return {
            "move_line_id": move_line.id,
            "picking_id": picking.id if picking else False,
            "product_id": move_line.product_id.id,
            "lot_id": move_line.lot_id.id if move_line.lot_id else False,
            "partner_id": (
                picking.partner_id.id if picking and picking.partner_id else False
            ),
            "responsible_id": self._get_responsible_id(picking),
            "analytic_account_id": self._get_analytic_account_id(move_line),
            "date": move_line.date,
            "qty_done": move_line.qty_done,
            "returned_qty": move_line.qty_done - net_qty,
            "net_qty": net_qty,
            "product_uom_id": move_line.product_uom_id.id,
            "location_id": move_line.location_id.id,
            "location_dest_id": move_line.location_dest_id.id,
            "pricelist_id": self.pricelist_id.id if self.pricelist_id else False,
            "standard_price": move_line.product_id.standard_price,
            "unit_price": unit_price,
            "total_value": net_qty * unit_price,
        }

    def action_generate_report(self):
        """Generate the devaluation report lines and open the report view."""
        self.ensure_one()
        report_model = self.env["stock.move.line.devaluation.report"]
        report_model.search([("create_uid", "=", self.env.uid)]).unlink()
        domain = self._get_move_line_domain()
        move_lines = self.env["stock.move.line"].search(domain)
        vals_list = []
        for ml in move_lines:
            net_qty = self._compute_net_qty(ml)
            if net_qty <= 0:
                continue
            unit_price = self._get_unit_price(ml.product_id, net_qty, ml.date)
            vals_list.append(self._prepare_report_line(ml, net_qty, unit_price))
        if not vals_list:
            raise UserError(
                _(
                    "No stock withdrawal lines found for the selected "
                    "criteria. Please adjust the filters and try again."
                )
            )
        report_model.create(vals_list)
        return {
            "name": _("Stock Withdrawal Valuation"),
            "type": "ir.actions.act_window",
            "res_model": "stock.move.line.devaluation.report",
            "view_mode": "tree,pivot",
            "domain": [("create_uid", "=", self.env.uid)],
            "context": dict(self.env.context, group_by=["analytic_account_id"]),
            "target": "current",
        }
