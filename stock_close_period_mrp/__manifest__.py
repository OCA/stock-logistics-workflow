# Copyright (C) 2023-Today:
# Dinamiche Aziendali Srl (<http://www.dinamicheaziendali.it/>)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Giuseppe Borruso <gborruso@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Close Period - MRP",
    "version": "16.0.1.0.0",
    "author": "Pordenone Linux User Group (PNLUG), Odoo Community Association (OCA), "
    "Dinamiche Aziendali srl, Sergio Corato",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "maintainers": ["MarcoCalcagni", "Borruso"],
    "depends": [
        "stock_close_period",
        "mrp",
    ],
    "data": [
        "views/stock_close_views.xml",
    ],
    "installable": True,
    "auto_install": True,
}
