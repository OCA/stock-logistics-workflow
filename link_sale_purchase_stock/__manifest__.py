# Copyright 2020 KEMA SK, s.r.o. - Radovan Skolnik <radovan@skolnik.info>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MTO Sale <-> Purchase",
    "version": "13.0.1.0.0",
    "category": "Hidden",
    "summary": "SO/PO relation in case of MTO",
    "author": "Radovan Skolnik, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["sale_stock", "purchase_stock", "sale_purchase", "stock_dropshipping"],
    "license": "AGPL-3",
    "data": ["views/sale_order_views.xml", "views/purchase_order_views.xml"],
    "demo": [],
    "qweb": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
