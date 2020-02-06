# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Picking Sale Order Link",
    "summary": "Link between picking and sale order",
    "version": "12.0.1.0.0",
    "category": "Inventory",
    "website": "http://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_stock"],
    "data": ["views/stock_picking_view.xml"],
}
