# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MassScrap(models.TransientModel):
    _name = "mass.scrap"
    _description = "Mass scrap"

    date_expiration_to_scrap = fields.Datetime(
        default=lambda self: fields.Datetime.now(),
        required=True,
        string="Expiration date to scrap",
        help="All the serial numbers/lots with an expiration date "
        "inferior to this date will be scrapped",
    )
    scrap_location_id = fields.Many2one(
        comodel_name="stock.location",
        domain="[('scrap_location', '=', True)]",
        default=lambda self: self.env["stock.location"].search(
            [("scrap_location", "=", True)], limit=1
        ),
        required=True,
    )
    specific_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        help="If you choose a warehouse here, only the serial numbers/lots "
        "currently stored in this warehouse will be scrapped",
    )
    stock_quant_ids = fields.Many2many(comodel_name="stock.quant", readonly=True)

    def _get_domain(self):
        domain = [
            ("quantity", ">", "0"),
            ("location_id.usage", "=", "internal"),
            ("lot_id.expiration_date", "<=", self.date_expiration_to_scrap),
        ]
        if self.specific_warehouse_id:
            domain.append(
                (
                    "location_id",
                    "child_of",
                    self.specific_warehouse_id.view_location_id.ids,
                )
            )
        return domain

    @api.onchange(
        "date_expiration_to_scrap",
        "scrap_location_id",
        "specific_warehouse_id",
    )
    def onchange_quants_to_scrap(self):
        if self.date_expiration_to_scrap:
            domain = self._get_domain()
            quants = self.env["stock.quant"].search_read(domain=domain, fields=["id"])
            quant_ids = [p["id"] for p in quants]
        else:
            quant_ids = []
        self.stock_quant_ids = [(6, False, quant_ids)]

    def _get_scrap_values(self, quant):
        return {
            "product_id": quant.product_id.id,
            "lot_id": quant.lot_id.id,
            "scrap_qty": quant.quantity,
            "product_uom_id": quant.product_uom_id.id,
            "location_id": quant.location_id.id,
            "scrap_location_id": self.scrap_location_id.id,
            "state": "draft",
        }

    def button_confirm(self):
        """
        Create a scrap for each selected quant.
        """
        self.ensure_one()
        # Call on change to load quants to scrap
        self.onchange_quants_to_scrap()

        scrap_model = self.env["stock.scrap"]
        scrap_ids = []
        for quant in self.stock_quant_ids:
            scrap = scrap_model.create(self._get_scrap_values(quant))
            scrap_ids.append(scrap.id)

        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_stock_scrap")
        action["domain"] = [("id", "in", scrap_ids)]
        return action
