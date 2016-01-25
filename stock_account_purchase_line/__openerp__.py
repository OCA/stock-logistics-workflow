# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Account Purchase Line",
    "summary": "Introduces the PO line to invoice line and account move line",
    "version": "8.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services, S.L., "
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Generic",
    "depends": ["account", "purchase"],
    "license": "AGPL-3",
    "data": [
        "views/account_move_view.xml",
        "views/account_invoice_view.xml",
    ],
    'installable': True,
}
