# Copyright (C) 2023-Today:
# Dinamiche Aziendali Srl (<http://www.dinamicheaziendali.it/>)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Giuseppe Borruso <gborruso@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime, time

from odoo import _, api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class StockClosePeriod(models.Model):
    _name = "stock.close.period"
    _description = "Stock Close Period"

    name = fields.Char(
        string="Reference",
        readonly=True,
        required=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    line_ids = fields.One2many(
        "stock.close.period.line",
        "close_id",
        string="Product",
        copy=True,
        readonly=False,
        states={"done": [("readonly", True)]},
    )
    no_recompute_lines = fields.Boolean(
        string="Do not recompute lines",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "In Progress"),
            ("done", "Validated"),
            ("cancel", "Cancelled"),
        ],
        copy=False,
        index=True,
        readonly=True,
        default="draft",
        string="Status",
    )
    close_date = fields.Date(
        readonly=True,
        required=True,
        default=fields.Date.context_today,
        states={"draft": [("readonly", False)]},
        help="The date that will be used for the store the product quantity and average"
        " cost.",
    )
    last_close_date = fields.Date(
        compute="_compute_last_close_date",
        store=True,
    )
    amount = fields.Float(string="Stock Amount Value", readonly=True, copy=False)
    work_start = fields.Datetime(readonly=True, default=fields.Datetime.now)
    work_end = fields.Datetime(readonly=True)
    force_evaluation_method = fields.Selection(
        [
            ("no_force", "Compute based category setup"),
            ("purchase", "Compute based purchase average cost"),
            ("standard", "Compute based cost in product"),
        ],
        default="no_force",
        copy=False,
        help="Force Evaluation method will be used only for compute purchase costs.",
    )
    last_closed_id = fields.Many2one(
        "stock.close.period",
        string="Last Closed",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    force_archive = fields.Boolean(
        default=False,
        help="Marks as archive the inventory move lines used during the process.",
    )
    purchase_ok = fields.Boolean(
        default=False,
        readonly=True,
        help="Marks if action 'Compute Purchase' is processed.",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    bypass_negative_qty = fields.Boolean(
        string="Bypass Negative Quantity",
        help="Ignore lines with negative quantity.",
    )

    def unlink(self):
        for closing in self:
            if closing.state in ["confirm", "done"]:
                raise UserError(
                    _(
                        "State in '%s'. You can only delete in state 'Draft' or 'Cancelled'."
                    )
                    % closing.state
                )
        return super(StockClosePeriod, self).unlink()

    def action_set_to_draft(self):
        for closing in self:
            if closing.state == "cancel":
                # clear data
                closing.line_ids.unlink()
                closing.state = "draft"
                closing.amount = 0
                closing.purchase_ok = False

    def _get_product_lines(self):
        self.ensure_one()
        # add all products active or not, of not service type,
        # if not set no_recompute_lines
        if not self.no_recompute_lines:
            self.line_ids = [
                (
                    0,
                    0,
                    dict(
                        close_id=self.id,
                        product_id=product.id,
                        product_code=product.default_code,
                        product_name=product.name,
                        product_uom_id=product.uom_id.id,
                        categ_name=product.categ_id.complete_name,
                        product_qty=0,
                        price_unit=0,
                        company_id=product.company_id
                        and product.company_id.id
                        or False,
                    ),
                )
                for product in self.env["product.product"]
                .with_context(active_test=False)
                .search(
                    [
                        ("type", "!=", "service"),
                    ]
                )
            ]

        # get quantity on end period for each product
        for closing_line_id in self.line_ids:
            product_id = closing_line_id.product_id
            list_product_qty = product_id._compute_qty_available(self.close_date)
            count = 0
            for line in list_product_qty:
                if count == 0:
                    closing_line_id.product_qty = line["stock_at_date"]
                    closing_line_id.location_id = line["location_id"]
                    closing_line_id.lot_id = line["lot_id"]
                    closing_line_id.owner_id = line["owner_id"]
                else:
                    self.env["stock.close.period.line"].create(
                        {
                            "close_id": self.id,
                            "product_id": line["product_id"],
                            "product_uom_id": line["uom_id"],
                            "product_qty": line["stock_at_date"],
                            "location_id": line["location_id"],
                            "lot_id": line["lot_id"],
                            "owner_id": line["owner_id"],
                            "price_unit": 0,
                        }
                    )
                count += 1

    @api.depends("last_closed_id.close_date")
    def _compute_last_close_date(self):
        for close in self:
            last_close_date = close.last_closed_id.close_date
            if not last_close_date:
                last_close_date = (
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("stock_close_period.last_close_date")
                )
            close.last_close_date = last_close_date

    def action_start(self):
        for closing in self.filtered(lambda x: x.state not in ("done", "cancel")):
            # add product line
            closing._get_product_lines()
            # set confirm status
            closing.state = "confirm"
        return True

    def _check_qty_available(self):
        self.ensure_one()

        # if a negative value, can't continue
        negative = self.line_ids.filtered(lambda x: x.product_qty < 0)
        if negative:
            res = False
        else:
            res = True
        return res

    def _deactivate_moves(self):
        self.ensure_one()

        # set active = False on stock_move and stock_move_line
        close_date = self.close_date or datetime.combine(self.close_date, time.max)

        self.env.cr.execute(
            """
            UPDATE
                stock_move
            SET
                active = false
            WHERE
                date <= date(%s)
                AND state = 'done'
                AND (
                    company_id == %s
                    OR company_id IS NULL
                );
            """,
            (close_date, self.company_id.id),
        )

        self.env.cr.execute(
            """
            UPDATE
                stock_move_line
            SET
                active = false
            WHERE
                date <= date(%s)
                AND state = 'done'
                AND (
                    company_id == %s
                    OR company_id IS NULL
                );
            """,
            (close_date, self.company_id.id),
        )

        return True

    def action_recalculate_purchase(self):
        for closing in self:
            if not closing.bypass_negative_qty and not closing._check_qty_available():
                raise UserError(
                    _(
                        "It's not possible to continue the execution."
                        "There are products with quantities < 0."
                    )
                )

            self.env["stock.move.line"].recompute_average_cost_period_purchase(closing)
            closing.purchase_ok = True
            if closing.force_archive:
                closing._deactivate_moves()
            closing.work_end = datetime.now()
        return True

    def action_cancel(self):
        for closing in self:
            closing.state = "cancel"
        return True

    def action_force_done(self):
        for closing in self:
            closing.state = "done"
            closing.amount = sum(closing.mapped("line_ids.amount_line"))

    def action_done(self):
        for closing in self:
            closing.state = "done"
            closing.amount = sum(closing.mapped("line_ids.amount_line"))
            if closing.bypass_negative_qty:
                closing.line_ids.filtered(lambda x: x.product_qty <= 0).unlink()
            else:
                closing.line_ids.filtered(
                    lambda x: x.product_qty == 0 and x.price_unit == 0
                ).unlink()
        return True

    def action_recompute_amount(self):
        for closing in self:
            closing.amount = sum(closing.mapped("line_ids.amount_line"))
