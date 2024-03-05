# Copyright 2022 Camptocamp SA, Trobz
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, fields, models


class ProductLabelLayout(models.TransientModel):
    _name = "product.label.layout"
    _inherit = ["product.label.layout", "base.selection.mixin"]

    def get_default_print_format_id(self):
        return self.get_default_selection("print_format_id")

    print_format = fields.Char(related="print_format_id.code")
    print_format_id = fields.Many2one(
        "base.selection",
        domain=[("field_id.model", "=", "product.label.layout")],
        string="Format",
        default=get_default_print_format_id,
        required=True,
    )

    @api.depends("print_format", "print_format_id")
    def _compute_dimensions(self):
        return super()._compute_dimensions()

    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()
        vals = self._get_print_format_data().get(self.print_format)
        if vals:
            data.update(vals)
        return xml_id, data

    def _get_print_format_data(self):
        """
        This is just an example. Can be overriden to provide data for other
        format(s) instead of modifying template.
        """
        return {
            "2x7xprice": {
                "report_to_call": "product.report_simple_label2x7",
                "padding_page": "padding: 14mm 3mm",
            }
        }
