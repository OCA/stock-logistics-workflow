# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Batch Creation",
    "summary": """
        Create a batch of pickings to be processed all together""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/wms",
    "category": "Warehouse Management",
    "application": False,
    "installable": True,
    "depends": [
        "product_packaging_dimension",  # OCA/product-attribute
        "product_dimension",
        "product_total_weight_from_packaging",  # OCA/product-attribute
        "stock",
        "stock_packaging_calculator",  # OCA/stock-logistics-warehouse
        "stock_picking_wave",
    ],
    "data": [
        "views/stock_device_type.xml",
        "views/stock_picking_wave.xml",
        "views/stock_picking.xml",
        "wizards/make_picking_batch.xml",
        "security/ir.model.access.csv",
    ],
    "development_status": "Alpha",
}
