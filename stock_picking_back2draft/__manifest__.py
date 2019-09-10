# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Pickings back to draft",
    "summary": "Reopen cancelled pickings",
    "version": "12.0.1.0.0",
    "category": "Warehouse Management",
    "website": "https://www.agilebg.com",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        'views/picking_view.xml',
    ],
    'images': ['images/picking.png'],
}
