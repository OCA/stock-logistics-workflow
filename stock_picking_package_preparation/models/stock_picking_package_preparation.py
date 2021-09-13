# Copyright 2015 Guewen Baconnier
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# Copyright 2016 Alessio Gerace - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class StockPickingPackagePreparation(models.Model):
    _name = "stock.picking.package.preparation"
    _description = "Package Preparation"
    _inherit = ["mail.thread"]

    FIELDS_STATES = {
        "done": [("readonly", True)],
        "in_pack": [("readonly", True)],
        "cancel": [("readonly", True)],
    }

    name = fields.Char(related="package_id.name", index=True, store=True,)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("cancel", "Cancelled"),
            ("in_pack", "In Pack"),
            ("done", "Done"),
        ],
        default="draft",
        string="State",
        readonly=True,
        copy=False,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        states=FIELDS_STATES,
    )
    picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        relation="stock_picking_pack_prepare_rel",
        column1="stock_picking_package_preparation_id",
        column2="stock_picking_id",
        string="Transfers",
        copy=False,
        states=FIELDS_STATES,
    )
    packaging_id = fields.Many2one(
        comodel_name="product.packaging", string="Packaging", states=FIELDS_STATES,
    )
    date = fields.Datetime(
        string="Document Date",
        default=fields.Datetime.now,
        states=FIELDS_STATES,
        copy=False,
    )
    date_done = fields.Datetime(string="Shipping Date", readonly=True, copy=False,)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        index=True,
        states=FIELDS_STATES,
        default=lambda s: s.env.company.id,
    )
    move_line_ids = fields.One2many(
        comodel_name="stock.move.line", compute="_compute_move_line_ids", readonly=True,
    )
    package_id = fields.Many2one(
        comodel_name="stock.quant.package", string="Pack", readonly=True, copy=False,
    )
    note = fields.Text()
    weight = fields.Float(
        compute="_compute_weight",
        help="The weight is computed when the " "preparation is done.",
    )
    quant_ids = fields.Many2many(
        compute="_compute_quant_ids",
        comodel_name="stock.quant",
        relation="stock_quant_pack_prepare_rel",
        column1="stock_picking_package_preparation_id",
        column2="stock_quant_id",
        string="All Content",
    )

    @api.depends("package_id")
    def _compute_quant_ids(self):
        for item in self:
            item.quant_ids = item.package_id._get_contained_quants()

    @api.depends("package_id", "package_id.quant_ids")
    def _compute_weight(self):
        for item in self:
            package = item.package_id
            if not package:
                continue
            quants = package._get_contained_quants()
            # weight of the products only
            item.weight = sum(l.product_id.weight * l.quantity for l in quants)

    @api.depends("picking_ids", "picking_ids.move_line_ids")
    def _compute_move_line_ids(self):
        for item in self:
            item.move_line_ids = item.mapped("picking_ids.move_line_ids")

    def action_done(self):
        if not self.mapped("package_id"):
            raise UserError(_("The package has not been generated."))
        for picking in self.picking_ids:
            picking.action_done()
        self.write({"state": "done", "date_done": fields.Datetime.now()})
        return True

    def action_cancel(self):
        if any(prep.state == "done" for prep in self):
            raise UserError(_("Cannot cancel a done package preparation."))
        package_ids = self.mapped("package_id")
        if package_ids:
            move_lines = self.env["stock.move.line"].search(
                [("result_package_id", "in", package_ids.ids)]
            )
            move_lines.write({"result_package_id": False})
            package_ids.unlink()
        self.write({"state": "cancel"})
        return True

    def action_draft(self):
        if any(prep.state != "cancel" for prep in self):
            raise UserError(
                _("Only canceled package preparations can be reset to draft.")
            )
        self.write({"state": "draft"})
        return True

    def action_put_in_pack(self):
        self._generate_pack()
        self.write({"state": "in_pack"})
        return True

    def _prepare_package(self):
        self.ensure_one()
        if not self.picking_ids:
            raise UserError(_("No transfer selected for this preparation."))
        location = self.mapped("picking_ids.location_dest_id")
        if len(location) > 1:
            raise UserError(
                _("All the transfers must have the same destination location")
            )
        values = {
            "packaging_id": self.packaging_id.id,
            "location_id": location.id,
        }
        return values

    def _generate_pack(self):
        pack_model = self.env["stock.quant.package"]
        move_line_model = self.env["stock.move.line"]
        for item in self:
            if any(picking.state != "assigned" for picking in item.picking_ids):
                raise UserError(_('All the transfers must be "Ready to Transfer".'))

            move_lines = move_line_model.browse()
            for picking in item.picking_ids:
                if not picking.move_line_ids:
                    picking.action_assign()
                move_lines |= picking.move_line_ids

            # If the stock.move.line has no processed quantity,
            # set it equal to the initial demand
            for move_line in move_lines:
                if float_is_zero(
                    move_line.qty_done,
                    precision_rounding=move_line.product_uom_id.rounding,
                ):
                    move_line.qty_done = move_line.product_qty

            pack = pack_model.create(item._prepare_package())

            move_lines.write({"result_package_id": pack.id})
            item.package_id = pack.id
