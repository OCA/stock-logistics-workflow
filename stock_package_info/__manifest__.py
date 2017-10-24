# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Package Info",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Tecnativa, "
              "LasLabs, "
              "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "category": "Inventory, Logistic, Storage",
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "depends": [
        "base_locale_uom_default",
        "sale",
        "stock",
    ],
    "data": [
        "data/ir_sequence_data.xml",
        "views/product_packaging_view.xml",
        "views/product_template_view.xml",
        "views/product_packaging_template_view.xml",
        "views/stock_picking_view.xml",
        "views/stock_quant_package_view.xml",
        "security/ir.model.access.csv",
        "reports/label_creator_palet_report.xml",
    ],
}
