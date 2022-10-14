# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo import models
from odoo.osv.expression import AND, OR
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.models.ir_ui_view import (
    transfer_modifiers_to_node,
    transfer_node_to_modifiers,
)


class StockPutawayRule(models.Model):
    _inherit = "stock.putaway.rule"

    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if result["name"] == "stock.putaway.rule.tree":
            result["arch"] = self._fields_view_get_adapt_attrs(result["arch"])
        return result

    def _fields_view_get_add_exclusive_selection_attrs(self, doc):
        """Make the readonly and required attrs dynamic for putaway rules

        By default, product_id and category_id fields have static domains
        such as they are mutually exclusive: both fields are required,
        as soon as we select a product, the category becomes readonly and
        not required, if we select a category, the product becomes readonly
        and not required.

        If we add a third field, such as "route_id", the domains for the
        readonly and required attrs should now include "route_id" as well,
        and if we add a fourth field, again. We can't extend them this way
        from XML, so this method dynamically generate these domains and
        set it on the fields attrs.

        The only requirement is to have exclusive_selection set in the options
        of the field:

        ::

            <field name="route_id"
                options="{'no_create': True, 'no_open': True,
                          'exclusive_selection': True}"
                readonly="context.get('putaway_route', False)"
                force_save="1"
            />

        Look in module stock_putaway_by_route (where this is tested as well).
        """
        exclusive_fields = set()
        nodes = doc.xpath("//field[@options]")
        for field in nodes:
            options = safe_eval(field.attrib.get("options", "{}"))
            if options.get("exclusive_selection"):
                exclusive_fields.add(field)

        for field in exclusive_fields:
            readonly_domain = OR(
                [
                    [(other.attrib["name"], "!=", False)]
                    for other in exclusive_fields
                    if other != field
                ]
            )
            required_domain = AND(
                [
                    [(other.attrib["name"], "=", False)]
                    for other in exclusive_fields
                    if other != field
                ]
            )

            if field.attrib.get("attrs"):
                attrs = safe_eval(field.attrib["attrs"])
            else:
                attrs = {}
            attrs["readonly"] = readonly_domain
            attrs["required"] = required_domain

            field.set("attrs", str(attrs))
            modifiers = {}
            transfer_node_to_modifiers(field, modifiers, context=self.env.context)
            transfer_modifiers_to_node(modifiers, field)

    def _add_exclusive_selection(self, doc, field_name):
        nodes = doc.xpath("//field[@name='{}']".format(field_name))
        for field in nodes:
            options = safe_eval(field.attrib.get("options", "{}"))
            options["exclusive_selection"] = True
            field.set("options", str(options))

    def _fields_view_get_adapt_attrs(self, view_arch):
        doc = etree.XML(view_arch)
        # Add the "exclusive_selection" option on product_id and category_id
        # fields from core, so they are treated by
        # _fields_view_get_add_exclusive_selection_attrs
        self._add_exclusive_selection(doc, "product_id")
        self._add_exclusive_selection(doc, "category_id")

        self._fields_view_get_add_exclusive_selection_attrs(doc)

        new_view = etree.tostring(doc, encoding="unicode")
        return new_view
