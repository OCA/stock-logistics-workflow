# Copyright 2012-2014 Alexandre Fayolle, Camptocamp SA
# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPickingBatch(models.Model):
    """This object allow to manage multiple stock.picking at the same time."""

    _inherit = "stock.picking.batch"

    name = fields.Char(
        index=True,
    )
    date = fields.Date(
        required=True,
        index=True,
        default=fields.Date.context_today,
        help="date on which the batch picking is to be processed",
    )
    user_id = fields.Many2one(index=True)
    use_oca_batch_validation = fields.Boolean(
        default=lambda self: self.env.company.use_oca_batch_validation,
        copy=False,
    )
    active_picking_ids = fields.One2many(
        string="Active Pickings",
        comodel_name="stock.picking",
        inverse_name="batch_id",
        readonly=True,
        domain=[("state", "not in", ("cancel", "done"))],
        help="List of active picking managed by this batch.",
    )
    notes = fields.Text(help="free form remarks")
    picking_count = fields.Integer(
        string="# Pickings",
        compute="_compute_picking_count",
    )
    split_transfers_from_batch = fields.Boolean(
        compute="_compute_split_transfers_from_batch",
        copy=False,
    )

    @api.depends_context("company")
    def _compute_split_transfers_from_batch(self):
        for batch in self:
            batch.split_transfers_from_batch = (
                batch.env.company.split_transfers_from_batch
            )

    def _compute_picking_count(self):
        """Calculate number of pickings."""
        counts = dict(
            self.env["stock.picking"]._read_group(
                [("batch_id", "in", self.ids)], ["batch_id"], ["__count"]
            )
        )
        for batch in self:
            batch.picking_count = counts.get(batch, 0)

    def action_cancel(self):
        """Call action_cancel for all batches pickings
        and set batches states to cancel too only if user set OCA batch validation
        approach.
        """
        if self.env.company.use_oca_batch_validation:
            self.mapped("picking_ids").action_cancel()
            self.state = "cancel"
        else:
            return super().action_cancel()

    def action_print_picking(self):
        pickings = self.mapped("picking_ids")
        if not pickings:
            raise UserError(_("Nothing to print."))
        return self.env.ref("stock.action_report_delivery").report_action(
            self.picking_ids
        )

    def remove_undone_pickings(self):
        """Remove of this batch all pickings which state is not done / cancel."""
        self.mapped("active_picking_ids").write({"batch_id": False})

    def action_view_stock_picking(self):
        """This function returns an action that display existing pickings of
        given batch picking.
        """
        self.ensure_one()
        pickings = self.mapped("picking_ids")
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        action["domain"] = [("id", "in", pickings.ids)]
        return action

    def action_picking_move_tree(self):
        action = self.picking_ids.action_picking_move_tree()
        action["views"] = [
            (
                self.env.ref("stock_picking_batch.view_picking_move_tree_inherited").id,
                "tree",
            ),
        ]
        return action

    def action_picking_move_line_tree(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.stock_move_line_action"
        )
        action["views"] = [
            (
                self.env.ref("stock_picking_batch_extended.view_move_line_tree").id,
                "tree",
            ),
        ]
        ctx = self.env.context.copy()
        ctx.update({"create": False})
        action["context"] = ctx
        action["context"]["parent"] = self
        action["domain"] = [("id", "in", self.move_line_ids.ids)]
        return action

    def action_split_picking(self):
        view = self.env.ref(
            "stock_picking_batch_extended.split_picking_from_batch_view_form"
        )
        return {
            "name": _("Split pickings"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "split.picking.from.batch",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "context": dict(
                self.env.context,
                default_move_ids=self.mapped("move_ids.id"),
                default_picking_batch_id=self.id,
            ),
        }
