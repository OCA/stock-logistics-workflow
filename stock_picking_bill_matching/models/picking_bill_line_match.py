# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError

_logger = __import__("logging").getLogger(__name__)

MATCHING_PRECISION = 0.001
MATCHING_EPSILON_SQL = 0.0001
INVOICE_STATE_INVOICED = "invoiced"
INVOICE_STATE_2B_INVOICED = "2binvoiced"


class PickingBillLineMatch(models.Model):
    _name = "picking.bill.line.match"
    _description = "Stock Move and Vendor Bill line matching view"
    _auto = False

    # STRICT ORDERING:
    # Matched vs Unmatched -> Product -> Vendor Bill vs Receipt -> Done vs Draft
    _order = "is_matched ASC, product_id, line_type DESC, is_done DESC"

    sm_id = fields.Many2one(comodel_name="stock.move", readonly=True)
    aml_id = fields.Many2one(comodel_name="account.move.line", readonly=True)

    company_id = fields.Many2one(comodel_name="res.company", readonly=True)
    partner_id = fields.Many2one(comodel_name="res.partner", readonly=True)
    product_id = fields.Many2one(comodel_name="product.product", readonly=True)

    line_qty = fields.Float("Initial Qty", readonly=True)
    unmatched_qty = fields.Float(readonly=True)
    is_matched = fields.Boolean(readonly=True)
    is_done = fields.Boolean("Is Done/Posted", readonly=True)
    line_type = fields.Selection(
        [("stock_move", "Receipt"), ("vendor_bill", "Vendor Bill")],
        string="Type",
        readonly=True,
    )

    line_uom_id = fields.Many2one(comodel_name="uom.uom", string="UoM", readonly=True)
    picking_id = fields.Many2one(comodel_name="stock.picking", readonly=True)
    account_move_id = fields.Many2one(comodel_name="account.move", readonly=True)

    line_amount_untaxed = fields.Monetary(readonly=True)
    currency_id = fields.Many2one(comodel_name="res.currency", readonly=True)
    state = fields.Char(readonly=True)
    reference = fields.Char(compute="_compute_reference")

    matched_reference = fields.Char("Matched To", compute="_compute_matched_reference")

    # Generic Field for Duck-Typed SQL Grouping
    matching_reference = fields.Char("Match Ref.", readonly=True)

    @api.depends("picking_id.name", "account_move_id.name")
    def _compute_reference(self):
        for line in self:
            if line.picking_id:
                line.reference = line.picking_id.name
                if line.picking_id.origin:
                    line.reference += f" ({line.picking_id.origin})"
            elif line.account_move_id:
                line.reference = line.account_move_id.name
                if line.account_move_id.invoice_origin:
                    line.reference += f" ({line.account_move_id.invoice_origin})"

    @api.depends(
        "aml_id.move_line_ids.picking_id.name", "sm_id.invoice_line_ids.move_id.name"
    )
    def _compute_matched_reference(self):
        for rec in self:
            if rec.aml_id:
                rec.matched_reference = ", ".join(
                    rec.aml_id.move_line_ids.mapped("picking_id.name")
                )
            elif rec.sm_id:
                rec.matched_reference = ", ".join(
                    rec.sm_id.invoice_line_ids.mapped("move_id.name")
                )
            else:
                rec.matched_reference = ""

    @api.model
    def _get_duck_typed_sql_ref(self, model_name, alias):
        """Safely check if an extension module injected a custom matching reference method."""
        model = self.env[model_name]
        if hasattr(model, "_get_bill_matching_reference_sql"):
            x = model._get_bill_matching_reference_sql(alias)
            _logger.debug("GET REF %s %s %s %s", self, model, alias, x)
            return x
        return "NULL::varchar"

    @api.model
    def _select_sm_line(self):
        ref_sql = self._get_duck_typed_sql_ref("stock.move", "sm")
        return f"""
            SELECT
                sm.id,
                sm.company_id,
                sp.partner_id,
                sm.product_id,
                sp.state,
                NULL AS currency_id,
                sm.product_uom_qty AS line_qty,
                sm.unmatched_qty AS unmatched_qty,
                (sm.product_uom_qty - COALESCE(sm.unmatched_qty, 0.0))
                    > {MATCHING_EPSILON_SQL} AS is_matched,
                sp.state = 'done' AS is_done,
                'stock_move' AS line_type,
                sm.product_uom AS line_uom_id,
                0 AS line_amount_untaxed,
                sm.id as sm_id,
                NULL as aml_id,
                sm.picking_id as picking_id,
                NULL as account_move_id,
                {ref_sql} AS matching_reference
            FROM
                stock_move sm
            JOIN
                stock_picking sp ON sm.picking_id = sp.id
            JOIN
                stock_picking_type pt ON sp.picking_type_id = pt.id
            JOIN
                product_product pp ON sm.product_id = pp.id
            JOIN
                product_template prod_tmpl ON pp.product_tmpl_id = prod_tmpl.id
            WHERE
                pt.code in ('incoming', 'outgoing')
                AND sm.state != 'cancel'
                AND prod_tmpl.type = 'product'
        """

    @api.model
    def _select_am_line(self):
        ref_sql = self._get_duck_typed_sql_ref("account.move.line", "aml")
        return f"""
            SELECT
                -aml.id as id,
                aml.company_id,
                aml.partner_id,
                aml.product_id,
                am.state,
                aml.currency_id,
                aml.quantity AS line_qty,
                aml.unmatched_qty AS unmatched_qty,
                (aml.quantity - COALESCE(aml.unmatched_qty, 0.0))
                    > {MATCHING_EPSILON_SQL} AS is_matched,
                am.state = 'posted' AS is_done,
                'vendor_bill' AS line_type,
                aml.product_uom_id AS line_uom_id,
                aml.price_subtotal AS line_amount_untaxed,
                NULL as sm_id,
                aml.id as aml_id,
                NULL as picking_id,
                aml.move_id as account_move_id,
                {ref_sql} AS matching_reference
            FROM
                account_move_line aml
            JOIN
                account_move am ON aml.move_id = am.id
            JOIN
                product_product pp ON aml.product_id = pp.id
            JOIN
                product_template prod_tmpl ON pp.product_tmpl_id = prod_tmpl.id
            WHERE
                aml.display_type = 'product'
                AND am.move_type in ('in_invoice', 'in_refund')
                AND am.state in ('draft', 'posted')
                AND prod_tmpl.type = 'product'
        """

    @property
    def _table_query(self):
        return "(%s) UNION ALL (%s)" % (self._select_sm_line(), self._select_am_line())

    def action_open_line(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move" if self.account_move_id else "stock.picking",
            "view_mode": "form",
            "target": "new",
            "res_id": self.account_move_id.id
            if self.account_move_id
            else self.picking_id.id,
        }

    def action_unmatch_lines(self):
        """DEBUG/UNDO: Easily sever the M2M links of selected lines."""

        affected_moves = self.env["stock.move"]
        for record in self:
            if record.aml_id:
                affected_moves |= record.aml_id.move_line_ids
                record.aml_id.write({"move_line_ids": [Command.clear()]})
            elif record.sm_id:
                affected_moves |= record.sm_id
                amls = self.env["account.move.line"].search(
                    [("move_line_ids", "in", record.sm_id.id)]
                )
                for aml in amls:
                    aml.write({"move_line_ids": [Command.unlink(record.sm_id.id)]})

        # Flush M2M changes to DB so unmatched_qty recomputes properly
        self.env.flush_all()

        # Duck Typing integration with the `stock_picking_invoicing` module:
        if hasattr(self.env["stock.move"], "invoice_state"):
            for move in affected_moves:
                move.invoice_state = (
                    INVOICE_STATE_INVOICED
                    if move.unmatched_qty <= MATCHING_PRECISION
                    else INVOICE_STATE_2B_INVOICED
                )
            for picking in affected_moves.mapped("picking_id"):
                picking.invoice_state = (
                    INVOICE_STATE_INVOICED
                    if all(
                        m.invoice_state == INVOICE_STATE_INVOICED
                        for m in picking.move_ids
                    )
                    else INVOICE_STATE_2B_INVOICED
                )

    @api.model
    def _get_matching_pairs(self, aml_lines, sm_lines):
        """
        Uses the visual `matching_reference` field.
        If an extension (like l10n_br) is installed, this will magically group by
        (Product + xPed/nItemPed). Otherwise, it seamlessly groups just by Product!
        """
        matches = []
        aml_by_key = defaultdict(lambda: self.env["account.move.line"])
        for line in aml_lines:
            key = (line.product_id, line.matching_reference)
            aml_by_key[key] |= line

        sm_by_key = defaultdict(lambda: self.env["stock.move"])
        for line in sm_lines:
            key = (line.product_id, line.matching_reference)
            sm_by_key[key] |= line

        for key, amls in aml_by_key.items():
            stock_moves_to_link = sm_by_key.get(key)
            if stock_moves_to_link:
                # Default Fallback: Match by product_id
                for aml in amls:
                    matches.append((aml, stock_moves_to_link))
        return matches

    def action_match_lines(self):
        if not self.sm_id and not self.aml_id:
            raise UserError(
                _("You must select at least one line to perform an action!")
            )

        if len(self.account_move_id) > 1:
            raise UserError(
                _("You cannot match lines from multiple Vendor Bills at once!")
            )

        pairs = self._get_matching_pairs(self.aml_id, self.sm_id)

        moves_to_receive = self.env["stock.move"]
        all_matched_moves = self.env["stock.move"]
        qty_to_set = {}

        for aml, stock_moves_to_link in pairs:
            remaining_to_match = aml.unmatched_qty
            for move in stock_moves_to_link.filtered(
                lambda m: m.state in ("draft", "confirmed", "assigned")
            ):
                if remaining_to_match <= MATCHING_PRECISION:
                    break
                qty_to_do = min(
                    remaining_to_match, move.product_uom_qty - move.quantity_done
                )
                if qty_to_do > 0:
                    qty_to_set[move] = qty_to_do
                    remaining_to_match -= qty_to_do
                    moves_to_receive |= move

            # 1. Establish the M2M links
            aml.move_line_ids = [Command.link(sm.id) for sm in stock_moves_to_link]

            all_matched_moves |= stock_moves_to_link

        # 2. Safely Process and Automate Receptions
        if moves_to_receive:
            pickings_to_process = moves_to_receive.mapped("picking_id")

            for picking in pickings_to_process:
                if picking.state == "draft":
                    picking.action_confirm()
                if picking.state not in ("assigned", "done"):
                    picking.action_assign()

            # Safely set the quantity done for what we are currently matching
            for move, qty in qty_to_set.items():
                move.quantity_done += qty

            # _action_done safely finalizes the moves and automatically creates
            # a backorder for anything not matched!
            pickings_to_process.with_context(cancel_backorder=False)._action_done()

        # Flush M2M changes to DB so unmatched_qty recomputes properly
        self.env.flush_all()

        # 3. Duck Typing integration with `stock_picking_invoicing`
        if hasattr(self.env["stock.move"], "invoice_state"):
            for move in all_matched_moves:
                move.invoice_state = (
                    INVOICE_STATE_INVOICED
                    if move.unmatched_qty <= MATCHING_PRECISION
                    else INVOICE_STATE_2B_INVOICED
                )
            for picking in all_matched_moves.mapped("picking_id"):
                picking.invoice_state = (
                    INVOICE_STATE_INVOICED
                    if all(
                        m.invoice_state == INVOICE_STATE_INVOICED
                        for m in picking.move_ids
                    )
                    else INVOICE_STATE_2B_INVOICED
                )

    def action_add_to_picking(self):
        records = self
        if not records:
            move_id = self.env.context.get("default_account_move_id")
            if move_id:
                records = self.search(
                    [
                        ("account_move_id", "=", move_id),
                        ("unmatched_qty", ">", MATCHING_PRECISION),
                    ]
                )

        if not records or not records.aml_id:
            raise UserError(_("No Vendor Bill lines found to add to a Picking."))

        return {
            "type": "ir.actions.act_window",
            "name": _("Create / Add to Picking"),
            "res_model": "bill.to.picking.wizard",
            "target": "new",
            "view_mode": "form",
            "context": {
                "default_partner_id": records[0].partner_id.id,
                "dialog_size": "medium",
                "active_model": "picking.bill.line.match",
                "active_ids": records.ids,
            },
        }
