from collections import defaultdict

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError


class PickingBillLineMatch(models.Model):
    _name = "picking.bill.line.match"
    _description = "Stock Move and Vendor Bill line matching view"
    _auto = False
    _order = "product_id, aml_id, sm_id"

    sm_id = fields.Many2one(comodel_name="stock.move", readonly=True)
    aml_id = fields.Many2one(comodel_name="account.move.line", readonly=True)

    company_id = fields.Many2one(comodel_name="res.company", readonly=True)
    partner_id = fields.Many2one(comodel_name="res.partner", readonly=True)
    product_id = fields.Many2one(comodel_name="product.product", readonly=True)
    line_qty = fields.Float("Quantity", readonly=True)
    unmatched_qty = fields.Float("Quantity", readonly=True)
    line_uom_id = fields.Many2one(comodel_name="uom.uom", string="UoM", readonly=True)

    picking_id = fields.Many2one(comodel_name="stock.picking", readonly=True)
    account_move_id = fields.Many2one(comodel_name="account.move", readonly=True)

    line_amount_untaxed = fields.Monetary(readonly=True)
    currency_id = fields.Many2one(comodel_name="res.currency", readonly=True)
    state = fields.Char(readonly=True)

    reference = fields.Char(compute="_compute_reference")

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

    def _get_common_select_fields(self):
        return """
            id,
            company_id,
            partner_id,
            product_id,
            state,
            currency_id,
            line_qty,
            line_uom_id,
            line_amount_untaxed
        """

    @api.model
    def _select_sm_line(self):
        return """
            SELECT
                sm.id,
                sm.company_id,
                sp.partner_id,
                sm.product_id,
                sp.state,
                NULL AS currency_id,
                sm.product_uom_qty AS line_qty,
                sm.unmatched_qty AS unmatched_qty,
                sm.product_uom AS line_uom_id,
                0 AS line_amount_untaxed,
                sm.id as sm_id,
                NULL as aml_id,
                sm.picking_id as picking_id,
                NULL as account_move_id
            FROM
                stock_move sm
            JOIN
                stock_picking sp ON sm.picking_id = sp.id
            JOIN
                stock_picking_type pt ON sp.picking_type_id = pt.id
            WHERE
                pt.code in ('incoming', 'outgoing')
                AND sm.state != 'cancel'
                AND sp.is_picking_matched IS False
        """  # NOTE: should be accept returns?

    @api.model
    def _select_am_line(self):
        return """
            SELECT
                -aml.id as id,
                aml.company_id,
                aml.partner_id,
                aml.product_id,
                am.state,
                aml.currency_id,
                aml.quantity AS line_qty,
                aml.unmatched_qty AS unmatched_qty,
                aml.product_uom_id AS line_uom_id,
                aml.price_subtotal AS line_amount_untaxed,
                NULL as sm_id,
                aml.id as aml_id,
                NULL as picking_id,
                aml.move_id as account_move_id
            FROM
                account_move_line aml
            JOIN
                account_move am ON aml.move_id = am.id
            WHERE
                aml.display_type = 'product'
                AND am.move_type in ('in_invoice', 'in_refund')
                AND am.state in ('draft', 'posted')
                AND am.is_picking_matched IS False
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

    @api.model
    def _action_create_bill_from_sm_lines(self, partner, stock_moves):
        if not partner:
            raise UserError(_("Cannot create a bill without a vendor."))

        bill = (
            self.env["account.move"]
            .with_context(default_move_type="in_invoice")
            .create(
                {
                    "partner_id": partner.id,
                    "invoice_date": fields.Date.context_today(self),
                }
            )
        )

        for move in stock_moves:
            self.env["account.move.line"].create(
                {
                    "move_id": bill.id,
                    "product_id": move.product_id.id,
                    "quantity": move.product_uom_qty,
                    "product_uom_id": move.product_uom.id,
                    "price_unit": move.purchase_line_id.price_unit
                    if move.purchase_line_id
                    else 0.0,
                    "move_line_ids": [(4, move.id)],
                }
            )

        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_in_invoice_type"
        )
        action.update(
            {
                "view_mode": "form",
                "res_id": bill.id,
                "views": [[self.env.ref("account.view_move_form").id, "form"]],
            }
        )
        return action

    def action_match_lines(self):
        """Match selected Stock Moves with selected Bill Lines."""
        if not self.sm_id and not self.aml_id:
            raise UserError(
                _("You must select at least one line to perform an action.")
            )

        if not self.aml_id:
            # Create a new bill from stock moves
            partner = self.sm_id.picking_id.partner_id
            return self._action_create_bill_from_sm_lines(partner, self.sm_id)

        if len(self.account_move_id) > 1:
            raise UserError(
                _("You cannot match lines from multiple Vendor Bills at once.")
            )

        # Group lines by product for matching
        aml_by_product = defaultdict(lambda: self.env["account.move.line"])
        for line in self.aml_id:
            aml_by_product[line.product_id] |= line

        sm_by_product = defaultdict(lambda: self.env["stock.move"])
        for line in self.sm_id:
            sm_by_product[line.product_id] |= line

        for product, am_lines in aml_by_product.items():
            stock_moves_to_link = sm_by_product.get(product)
            if stock_moves_to_link:
                # Link all selected stock moves for this product to the selected bill lines
                for aml in am_lines:
                    aml.move_line_ids = [
                        Command.link(sm.id) for sm in stock_moves_to_link
                    ]
                    for move in stock_moves_to_link.filtered(
                        lambda m: m.state in ("draft", "confirmed", "assigned")
                    ):
                        move.quantity_done = min(aml.quantity, move.product_uom_qty)
                stock_moves_to_link.mapped("picking_id").filtered(
                    lambda p: p.state in ("draft", "confirmed", "assigned")
                ).with_context(skip_backorder=True).button_validate()

    def action_add_to_picking(self):
        """Add selected bill lines to an existing or new picking."""
        if not self or not self.aml_id:
            raise UserError(
                _("Select at least one Vendor Bill line to add to a Picking.")
            )

        context = {
            "default_partner_id": self.partner_id.id,
            "dialog_size": "medium",
            "active_model": "picking.bill.line.match",
            "active_ids": self.ids,
        }
        return {
            "type": "ir.actions.act_window",
            "name": _("Add to Picking"),
            "res_model": "bill.to.picking.wizard",
            "target": "new",
            "view_mode": "form",
            "context": context,
        }
