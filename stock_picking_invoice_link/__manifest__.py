# Copyright 2013-17 Agile Business Group (<http://www.agilebg.com>)
# Copyright 2016 AvanzOSC (<http://www.avanzosc.es>)
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# Copyright 2021 Tecnativa - João Marques
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Stock Picking Invoice Link",
    "version": "18.0.2.0.0",
    "category": "Warehouse Management",
    "summary": "Adds link between pickings and invoices",
    "author": "Agile Business Group, "
    "Tecnativa, "
    "BCIM sprl, "
    "Softdil S.L, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "development_status": "Mature",
    "depends": ["stock_account"],
    "data": ["views/stock_view.xml", "views/account_invoice_view.xml"],
    "installable": True,
}
