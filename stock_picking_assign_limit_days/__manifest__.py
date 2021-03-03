# Copyright 2021 PlanetaTIC <info@planetatic.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Picking Assign Limit Days",
    "summary":
        "Do not assign a stock move until its expected date is below X days",
    "version": "12.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Stock",
    "website": "https://www.planetatic.com/",
    "author": "PlanetaTIC",
    "maintainers": ["PlanetaTIC"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock"
    ],
    "data": [
        'data/ir_config_parameter.xml',
    ],
}
