# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round


class StockPickingScrapLine(models.TransientModel):
    _name = "wiz.stock.picking.scrap.line"
    _description = "Wizard lines for picking whole scrap"
    _rec_name = "product_id"

    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", readonly=True
    )
    lot_id = fields.Many2one(comodel_name="stock.lot", string="Lot", readonly=True)
    package_id = fields.Many2one(
        comodel_name="stock.quant.package", string="Package", readonly=True
    )
    owner_id = fields.Many2one(
        comodel_name="res.partner", string="Owner", readonly=True
    )
    quantity = fields.Float(digits="Product Unit of Measure", required=True)
    uom_id = fields.Many2one(
        comodel_name="uom.uom", string="Unit of Measure", readonly=True
    )
    wizard_id = fields.Many2one(comodel_name="wiz.stock.picking.scrap", string="Wizard")
    move_line_id = fields.Many2one(comodel_name="stock.move.line", string="Move Line")
    should_replenish = fields.Boolean(
        string="Replenish Quantities",
        help="Trigger replenishment for scrapped products",
    )
    scrap_reason_tag_ids = fields.Many2many(
        comodel_name="stock.scrap.reason.tag", string="Scrap Reason"
    )


class StockPickingScrap(models.TransientModel):
    _name = "wiz.stock.picking.scrap"
    _description = "Picking Whole Scrap"

    picking_id = fields.Many2one(comodel_name="stock.picking")
    line_ids = fields.One2many(
        comodel_name="wiz.stock.picking.scrap.line",
        inverse_name="wizard_id",
        string="Moves",
    )
    scrap_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Scrap Location",
        domain=[("scrap_location", "=", True)],
    )

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get("active_ids", list())) > 1:
            raise UserError(self.env._("You may only scrap one picking at a time!"))
        res = super().default_get(fields)
        scrap_lines = []
        picking = self.env["stock.picking"].browse(self.env.context.get("active_id"))
        if picking:
            res.update({"picking_id": picking.id})
            if picking.state != "done":
                raise UserError(self.env._("You may only scrap pickings in done state"))
            for move_line in picking.move_line_ids:
                if move_line.move_id.scrapped:
                    continue
                quantity = move_line.quantity
                quantity = float_round(
                    quantity, precision_rounding=move_line.product_uom_id.rounding
                )
                scrap_lines.append(
                    (
                        0,
                        0,
                        {
                            "product_id": move_line.product_id.id,
                            "lot_id": move_line.lot_id.id,
                            "package_id": move_line.result_package_id.id,
                            "owner_id": move_line.owner_id.id,
                            "quantity": quantity,
                            "uom_id": move_line.product_uom_id.id,
                            "move_line_id": move_line.id,
                        },
                    )
                )
            if "line_ids" in fields:
                res.update({"line_ids": scrap_lines})
            if "scrap_location_id" in fields:
                scrap_location = self.env["stock.location"].search(
                    [("scrap_location", "=", True)], limit=1
                )
                res["scrap_location_id"] = scrap_location.id
        return res

    def _prepare_stock_scrap(self, scrap_line):
        vals = {
            "product_id": scrap_line.product_id.id,
            "product_uom_id": scrap_line.move_line_id.product_uom_id.id,
            "lot_id": scrap_line.move_line_id.lot_id.id,
            "package_id": scrap_line.move_line_id.result_package_id.id,
            "owner_id": scrap_line.move_line_id.owner_id.id,
            "picking_id": scrap_line.move_line_id.picking_id.id,
            "location_id": scrap_line.move_line_id.location_dest_id.id,
            "scrap_location_id": self.scrap_location_id.id,
            "scrap_qty": scrap_line.quantity,
            "should_replenish": scrap_line.should_replenish,
            "scrap_reason_tag_ids": [(6, 0, scrap_line.scrap_reason_tag_ids.ids)],
        }
        return vals

    def create_scrap(self):
        StockScrap = self.env["stock.scrap"]
        new_scraps = StockScrap.browse()
        for line in self.line_ids.filtered("quantity"):
            if (
                float_compare(
                    line.quantity,
                    line.move_line_id.quantity,
                    precision_rounding=line.product_id.uom_id.rounding,
                )
                > 0
            ):
                raise UserError(
                    self.env._("You can't scrap more quantity that done it")
                )
            new_scraps += StockScrap.create(self._prepare_stock_scrap(line))
        # import wdb; wdb.set_trace()
        new_scraps.do_scrap()
        return new_scraps
