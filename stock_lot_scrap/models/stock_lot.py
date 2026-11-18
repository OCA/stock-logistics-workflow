# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import Command, api, models
from odoo.exceptions import ValidationError


class StockLot(models.Model):
    _inherit = "stock.lot"

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        """Inject the button here to avoid conflicts with other modules
        that add a header element in the main view.
        """
        arch, view = super()._get_view(view_id, view_type, **options)
        if isinstance(arch, bytes):
            # If arch is bytes, convert it to an XML element
            eview = etree.fromstring(arch)
        else:
            # If arch is already an XML element, no need to parse
            eview = arch
        xml_header = eview.xpath("//header")
        if not xml_header:
            # Create a header
            header_element = etree.Element("header")
            # Append it to the view
            forms = eview.xpath("//form")
            if forms:
                forms[0].insert(0, header_element)
        else:
            header_element = xml_header[0]
        button_element = etree.Element(
            "button",
            {
                "type": "object",
                "name": "action_scrap_lot",
                "invisible": "product_qty == 0",
                "confirm": self.env._(
                    "This will scrap the whole lot. Are you sure you want to continue?"
                ),
                "string": self.env._("Scrap"),
            },
        )
        header_element.append(button_element)
        arch = eview  # Return the XML element directly
        return arch, view

    def _prepare_scrap_vals(self, quant):
        """Values of the scrap move (``stock.move`` with ``is_scrap``) for a quant.

        Since Odoo 20, scraps are stock moves flagged as ``is_scrap`` instead of
        ``stock.scrap`` records.
        """
        self.ensure_one()
        company = quant.company_id or self.env.company
        return {
            "origin": quant.lot_id.name,
            "product_id": quant.product_id.id,
            "uom_id": quant.product_id.uom_id.id,
            "product_uom_qty": quant.quantity,
            "location_id": quant.location_id.id,
            "location_dest_id": company.scrap_location_id.id,
            "company_id": company.id,
            "is_scrap": True,
            "state": "draft",
            "move_line_ids": [
                Command.create(
                    {
                        "product_id": quant.product_id.id,
                        "uom_id": quant.product_id.uom_id.id,
                        "quantity": quant.quantity,
                        "lot_id": self.id,
                        "package_id": quant.package_id.id,
                        "location_id": quant.location_id.id,
                        "location_dest_id": company.scrap_location_id.id,
                        "company_id": company.id,
                    }
                )
            ],
        }

    def action_scrap_lot(self):
        self.ensure_one()
        quants = self.quant_ids.filtered(
            lambda x: x.location_id.usage == "internal" and x.quantity > 0
        )
        if not quants:
            raise ValidationError(
                self.env._("This lot doesn't contain any quant in internal location."),
            )
        scraps = self.env["stock.move"].create(
            [self._prepare_scrap_vals(quant) for quant in quants]
        )
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.stock_scrapped_moves_action"
        )
        result["context"] = self.env.context
        if len(scraps) != 1:
            result["domain"] = [("id", "in", scraps.ids)]
        else:  # pragma: no cover
            result["views"] = [(self.env.ref("stock.view_scrap_move_form").id, "form")]
            result["res_id"] = scraps.id
        return result
