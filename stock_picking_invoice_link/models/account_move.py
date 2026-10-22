# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2015-2016 AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# Copyright 2020 Manuel Calero - Tecnativa
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import Command, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        string="Related Pickings",
        store=True,
        compute="_compute_picking_ids",
        help="Related pickings (only when the invoice has been generated from a sale "
        "order).",
    )

    picking_count = fields.Integer(
        string="Pickings count", compute="_compute_picking_count"
    )

    @api.depends("invoice_line_ids", "invoice_line_ids.move_line_ids")
    def _compute_picking_ids(self):
        for invoice in self:
            invoice.picking_ids = invoice.mapped(
                "invoice_line_ids.move_line_ids.picking_id"
            )

    @api.depends("picking_ids")
    def _compute_picking_count(self):
        for invoice in self:
            invoice.picking_count = len(invoice.picking_ids)

    def action_show_picking(self):
        """This function returns an action that display existing pickings
        of given invoice.
        It can either be a in a list or in a form view, if there is only
        one picking to show.
        """
        self.ensure_one()
        form_view_name = "stock.view_picking_form"
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        if len(self.picking_ids) > 1:
            result["domain"] = f"[('id', 'in', {self.picking_ids.ids})]"
        else:
            form_view = self.env.ref(form_view_name)
            result["views"] = [(form_view.id, "form")]
            result["res_id"] = self.picking_ids.id
        return result


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    move_line_ids = fields.Many2many(
        comodel_name="stock.move",
        relation="stock_move_invoice_line_rel",
        column1="invoice_line_id",
        column2="move_id",
        string="Related Stock Moves",
        readonly=True,
        copy=False,
        help="Related stock moves (only when the invoice has been"
        " generated from a sale order).",
    )

    def copy_data(self, default=None):
        """Copy the move_line_ids in case of refund invoice creating new invoices
        (refund_method="modify") for multiple records."""
        vals_list = super().copy_data(default)

        if self.env.context.get("force_copy_stock_moves"):
            for record, vals in zip(self, vals_list, strict=False):
                if "move_line_ids" not in vals and record.move_line_ids:
                    vals["move_line_ids"] = [Command.set(record.move_line_ids.ids)]

        return vals_list
