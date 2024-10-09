# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Weighable Product - Default Weight",
    "version": "12.0.1.0.0",
    "category": "Point Of Sale",
    "summary": "Set default weight on weighable product,"
    " the weight is guessed from the ratio of the unit of mesure",
    "author": "GRAP, Odoo Community Association (OCA)",
    "maintainers": ["legalsylvain"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "depends": ["product"],
    "demo": ["demo/res_groups.xml"],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
