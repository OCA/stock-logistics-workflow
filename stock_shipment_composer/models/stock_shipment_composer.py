# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockShipmentComposer(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _name = "stock.shipment.composer"
    _description = "Stock Shipment Composer"
    _order = "name desc"

    name = fields.Char(
        string="Shipment Composer",
        default="New",
        copy=False,
        required=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        check_company=True,
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
    )
    picking_type_id = fields.Many2one(
        "stock.picking.type", string="Operation Type", required=True
    )
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        tracking=True,
        check_company=True,
        readonly=True,
        states={"draft": [("readonly", False)], "in_progress": [("readonly", False)]},
        default=lambda self: self.env.user,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        readonly=True,
        index=True,
        default=lambda self: self.env.company,
    )
    line_ids = fields.One2many(
        "stock.shipment.composer.line", "composer_id", string="Shipment Composer Lines"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        compute="_compute_state",
        store=True,
        string="Status",
        default="draft",
        copy=False,
        tracking=True,
        required=True,
        readonly=True,
        index=True,
    )
    scheduled_date = fields.Datetime(
        compute="_compute_scheduled_date",
        store=True,
        readonly=False,
        copy=False,
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
        help="""Scheduled date for the transfers to be processed.
              - When moves are added/removed/updated then this will be their pickings'
                earliest scheduled date.
              - You can manually set a date as appropriate. However the updated value
                will not propagate to the related pickings.""",
    )
    move_ids = fields.Many2many("stock.move", compute="_compute_move_ids", store=True)
    show_check_availability = fields.Boolean(
        compute="_compute_move_ids",
        compute_sudo=True,
    )
    show_validate = fields.Boolean(compute="_compute_show_validate")
    date_done = fields.Datetime(
        "Date of Validation",
        compute="_compute_state",
        store=True,
        copy=False,
        readonly=True,
        help="Date at which the composer has been validated.",
    )

    @api.depends("move_ids", "move_ids.state")
    def _compute_state(self):
        recs = self.filtered(lambda x: x.state not in ["cancel", "done"])
        for rec in recs:
            if not rec.move_ids:
                continue
            if all(move.state == "cancel" for move in rec.move_ids):
                rec.state = "cancel"
                continue
            if rec.move_ids.filtered(
                lambda x: x.shipment_composer_id == rec
                and x.state in ["cancel", "done"]
            ):
                rec.state = "done"
                rec.date_done = fields.Datetime.now()

    @api.depends("line_ids", "line_ids.move_id.picking_id.scheduled_date")
    def _compute_scheduled_date(self):
        for rec in self:
            pickings = rec.line_ids.move_id.picking_id
            rec.scheduled_date = min(
                pickings.filtered("scheduled_date").mapped("scheduled_date"),
                default=False,
            )

    @api.depends("line_ids.move_id", "line_ids.move_id.state")
    def _compute_move_ids(self):
        for rec in self:
            rec.move_ids = rec.line_ids.move_id
            rec.show_check_availability = any(
                m.state not in ["assigned", "cancel", "done"] for m in rec.move_ids
            )

    def _compute_show_validate(self):
        for rec in self:
            rec.show_validate = False
            if rec.line_ids == rec.line_ids.filtered(
                lambda x: x.quantity > 0 and x.reserved_enough
            ):
                rec.show_validate = True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                company_id = vals.get("company_id", self.env.company.id)
                vals["name"] = (
                    self.env["ir.sequence"]
                    .with_company(company_id)
                    .next_by_code("stock.shipment.composer")
                    or "/"
                )
        return super().create(vals_list)

    def action_confirm(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("You have to add some shipment composer lines."))
        self.line_ids.move_id.picking_id.action_confirm()
        self._check_company()
        self.state = "in_progress"
        return True

    def action_assign(self):
        for rec in self:
            if rec.state == "draft":
                rec.action_confirm()
        moves = self.move_ids.filtered(
            lambda x: x.state not in ("draft", "cancel", "done")
        )
        moves.sorted(
            key=lambda x: (
                -int(x.priority),
                not bool(x.date_deadline),
                x.date_deadline,
                x.date,
                x.id,
            )
        )
        if not moves:
            raise UserError(_("Nothing to check the availability for."))
        moves._action_assign()
        return True

    def action_cancel(self):
        recs = self.filtered(lambda x: x.state in ["draft", "in_progress"])
        recs.state = "cancel"
        return True

    def action_draft(self):
        recs = self.filtered(lambda x: x.state in ["cancel"])
        recs.state = "draft"
        return True

    def action_done(self):
        self.ensure_one()
        if self.line_ids.filtered(lambda x: x.quantity == 0):
            raise UserError(
                _(
                    "You cannot validate a shipment composer with lines that have a "
                    "quantity of 0.",
                )
            )
        if self.line_ids.filtered(lambda x: x.quantity > x.reserved_availability):
            raise UserError(
                _(
                    "You cannot validate a shipment composer with lines that have a "
                    "quantity greater than the reserved availability.",
                )
            )
        pickings = self.move_ids.picking_id
        # First clear the qty_done of all move lines of related pickings
        pickings.move_line_ids.qty_done = 0.0
        # Then set the qty_done of each move line to the reserved quantity
        for line in self.line_ids:
            move = line.move_id
            unallocated_qty = line.quantity
            for ml in move.move_line_ids:
                ml.qty_done = min(ml.reserved_uom_qty, unallocated_qty)
                unallocated_qty -= ml.qty_done
        for picking in pickings:
            picking.message_post(
                body=_(
                    "<b>{label}:</b> {source} "
                    "<a href='#id={id}&amp;view_type=form&amp;model=stock.shipment.composer'>{doc}</a>"  # noqa B950
                ).format(
                    label=_("Transferred by"),
                    source=_("Shipment Composer"),
                    id=self.id,
                    doc=self.name,
                )
            )
        # Run sanity_check here and skip the one in button_validate().
        pickings._sanity_check(separate_pickings=False)
        # Set the composer on all moves of the pickings before validation
        self.move_ids.shipment_composer_id = self
        context = {"skip_sanity_check": True, "validated_by_composer": True}
        return pickings.with_context(skip_immediate=True, **context).button_validate()

    def action_view_operations(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_action")
        action["context"] = self.env.context
        action["domain"] = [("id", "in", self.move_ids.ids)]
        return action

    @api.ondelete(at_uninstall=False)
    def _unlink_except_draft_or_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "cancel"):
                raise UserError(
                    _(
                        "You can not delete a shipment composer unless the status is "
                        "Draft or Cancelled."
                    )
                )

    def _track_subtype(self, init_values):
        if "state" in init_values:
            return self.env.ref("stock_shipment_composer.mt_shipment_composer_state")
        return super()._track_subtype(init_values)
