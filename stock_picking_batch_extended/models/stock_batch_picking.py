# Copyright 2012-2014 Alexandre Fayolle, Camptocamp SA
# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPickingBatch(models.Model):
    """This object allow to manage multiple stock.picking at the same time."""

    # renamed stock.batch.picking -> stock.picking.batch
    _inherit = "stock.picking.batch"

    name = fields.Char(
        index=True,
        states={"draft": [("readonly", False)]},
    )
    date = fields.Date(
        required=True,
        readonly=True,
        index=True,
        states={"draft": [("readonly", False)], "in_progress": [("readonly", False)]},
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
    entire_package_ids = fields.Many2many(
        comodel_name="stock.quant.package",
        compute="_compute_entire_package_ids",
        help="Those are the entire packages of a picking shown in the view of "
        "operations",
    )
    entire_package_detail_ids = fields.Many2many(
        comodel_name="stock.quant.package",
        compute="_compute_entire_package_ids",
        help="Those are the entire packages of a picking shown in the view of "
        "detailed operations",
    )
    picking_count = fields.Integer(
        string="# Pickings",
        compute="_compute_picking_count",
    )

    @api.depends("picking_ids")
    def _compute_entire_package_ids(self):
        for batch in self:
            batch.update(
                {
                    "entire_package_ids": batch.use_oca_batch_validation
                    and batch.picking_ids.mapped("entire_package_ids" or False),
                    "entire_package_detail_ids": batch.use_oca_batch_validation
                    and batch.picking_ids.mapped("entire_package_detail_ids" or False),
                }
            )

    def _compute_picking_count(self):
        """Calculate number of pickings."""
        groups = self.env["stock.picking"].read_group(
            domain=[("batch_id", "in", self.ids)],
            fields=["batch_id"],
            groupby=["batch_id"],
        )
        counts = {g["batch_id"][0]: g["batch_id_count"] for g in groups}
        for batch in self:
            batch.picking_count = counts.get(batch.id, 0)

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
        return self.env.ref(
            "stock_picking_batch_extended.action_report_batch_picking"
        ).report_action(self)

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
