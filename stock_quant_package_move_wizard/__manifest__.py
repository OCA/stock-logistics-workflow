# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Quant & Package moving wizard",
    "summary": "Select a quant Move quants to another location in a few clicks",
    "category": "Inventory/Inventory",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["stock"],
    "author": "Odoo Community Association (OCA), "
    "AvanzOSC, "
    "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
    "Akretion",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
        "Alexis de Lattre <alexis.delattre@akretion.com>",
    ],
    "data": [
        # "wizards/quants_move_wizard_view.xml",
        "security/ir.model.access.csv",
        "wizards/stock_quant_move_wizard_view.xml",
        "views/stock_quant.xml",
        # "views/stock_quant_package.xml",
    ],
    "installable": True,
}
