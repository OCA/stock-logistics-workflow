# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    line_lot_name = fields.Char(
        string="Lot Name",
        compute="_compute_line_lot_name",
        inverse="_inverse_line_lot_name",
    )
    life_date = fields.Datetime(
        string="End of Life Date",
        help="This is the date on which the goods with this Serial Number may "
        "become dangerous and must not be consumed.",
        compute="_compute_life_date",
        inverse="_inverse_life_date",
    )

    @api.onchange("line_lot_name")
    def onchange_line_lot_name(self):
        lot = self.production_lot_from_name(create_lot=False)
        self.life_date = lot.life_date

    def _compute_line_lot_name(self):
        for line in self:
            line.line_lot_name = ", ".join(
                lot.name for lot in line.mapped("move_line_ids.lot_id")
            )

    def _inverse_line_lot_name(self):
        for line in self:
            if not line.line_lot_name:
                continue
            lot = line.production_lot_from_name()
            if line.move_line_ids:
                if line.move_line_ids.lot_id != lot:
                    line.move_line_ids.lot_id = lot

    def _compute_life_date(self):
        for line in self:
            line.life_date = line.move_line_ids[:1].lot_id.life_date

    def _inverse_life_date(self):
        for line in self:
            if not line.life_date:
                continue
            lot = line.production_lot_from_name()
            if lot and lot.life_date != line.life_date:
                lot.life_date = line.life_date

    def production_lot_from_name(self, create_lot=True):
        StockProductionLot = self.env["stock.production.lot"]
        if not self.line_lot_name:
            if self.move_line_ids:
                raise ValidationError(_("Open detail to remove lot"))
            else:
                return StockProductionLot.browse()
        if len(self.move_line_ids) > 1:
            raise ValidationError(_("Go to lots to change data"))
        lot = StockProductionLot.search(
            [
                ("product_id", "=", self.product_id.id),
                ("name", "=", self.line_lot_name),
            ],
            limit=1,
        )
        if not lot and create_lot:
            lot = lot.create(
                {
                    "name": self.line_lot_name,
                    "product_id": self.product_id.id,
                    "life_date": self.life_date,
                    "company_id": self.company_id.id,
                }
            )
        return lot
