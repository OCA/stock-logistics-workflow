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
    expiration_date = fields.Datetime(
        string="End of Life Date",
        help="This is the date on which the goods with this Serial Number may "
        "become dangerous and must not be consumed.",
        compute="_compute_expiration_date",
        inverse="_inverse_expiration_date",
    )

    @api.onchange("line_lot_name")
    def onchange_line_lot_name(self):
        lot = self.production_lot_from_name(create_lot=False)
        self.expiration_date = lot.expiration_date

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

    def _compute_expiration_date(self):
        for line in self:
            line.expiration_date = line.move_line_ids[:1].lot_id.expiration_date

    def _inverse_expiration_date(self):
        for line in self:
            if not line.expiration_date:
                continue
            lot = line.production_lot_from_name()
            if lot and lot.expiration_date != line.expiration_date:
                lot.expiration_date = line.expiration_date

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
                    "expiration_date": self.expiration_date,
                    "company_id": self.company_id.id,
                }
            )
        return lot
