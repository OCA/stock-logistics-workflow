#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock picking group batch",
    "summary": "Manage product quantities in batch transfers.",
    "version": "16.0.1.0.0",
    "website": "https://github.com/OCA/stock-logistics-workflow"
    "/tree/16.0/stock_picking_batch_grouped",
    "author": "Aion Tech, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": [
        "SirAionTech",
    ],
    "category": "Warehouse Management",
    "depends": [
        "stock",
        "stock_picking_batch",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/stock_picking_batch_grouped_security.xml",
        "views/stock_picking_batch_views.xml",
    ],
}
