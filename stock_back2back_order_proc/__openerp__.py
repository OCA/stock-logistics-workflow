# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
#            Alex Duan <alex.duan@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Stock Back-to-back orders',
    'version': '1.0',
    'category': 'Warehouse',
    'description': """
This module aims to change the original back-order logic of Odoo
in chained locations introducing true back-to-back orders.


STANDARD ODOO BACK-TO-BACK ORDER BEHAVIOR:
Original behavior is not fully suitable to handle back-to-back backorders
    process (check "back-to-back orders comparison.pdf"):
eg: Let's take the following example to understand the implemented difference:
- One PO from a supplier for the full quantity (eg 100 PCE) and
    your supplier ships immediately
    only the available quantity which is 70 PCE.
- 30 PCE are to be shipped later on.
- Setup with following chained location:
    SUPPLIER => TRANSIT (Chained/Manual) => INPUT locations

When PO is validated to TRANSIT location,
- DN1 is created for 100 PCE (SUPPLIER to TRANSIT)
- chained move DN2 is automatically created for 100 PCE (from TRANSIT to INPUT)
When only partial quantity is shipped (eg 70 PCE):
- DN1 is processed and shipped for 70 PCE (done state)
- DN2 is kept with 100 PCE
    (in waiting state "waiting that all replenishments
        arrive at location before shipping")
- chained move DN3 is automatically created with 30 PCE
    (from SUPPLIER to TRANSIT) as back order of DN1.

Several drawbacks make current behavior unappropriate:
- Stock in the different locations are not reflecting real stocks.
- This is due to the fact that original delivery note is kept in waiting state
    in input or output location until all incoming chained DN are processed.
- For this reason as well, real stock in the warehouse is incorrect in our case
    and is only correct when all backorders are shipped
    impacting company stock visibility.
- Documents (DN) are not following actual flow (one document missing)


ENHANCED BACK-TO-BACK ORDER BEHAVIOR
This modules replace standard Odoo behavior
    by an enhanced back-to-back order workflow with the following behavior:
- Within a chained location structure,
    all chained moves will be created for the full quantity (eg: 100 PCE),
    following standard OE behavior.
    (for how many chained location that has been created:
        if a second location is chained, an additional chained move is created)
- Nevertheless, when a partial quantity is shipped
    in the original delivery note
    (eg: 70 PCE), all related chained moves are updated with this new quantity
    (70 PCES) for as many level as necessary
    (difference with standard behavior).
- Backorders and related chained moves are
    created with the remaining quantities (eg: 30 PCE)
- Automated and manual chained behavior are respected.


Taking back our previous example:

When PO is validated to TRANSIT location,
- DN1 is created for 100 PCE (SUPPLIER to TRANSIT)
- chained move DN2 is automatically created for 100 PCE (from TRANSIT to INPUT)
When only partial quantity is shipped (eg 70 PCE):
- DN1 is shipped to 70 PCE (done state)
- DN2 is kept with 100 PCE
    (in waiting state "waiting that all replenishments
        arrive at location before shipping")
- chained move DN3 is automatically created with 30 PCE
    (from SUPPLIER to TRANSIT)

When DN1 is partially shipped with 70 PCE:
- DN2 quantity is changed to 70 PCE
    (and depending on stock marked as available
        since in our example it is set as manual).
If automatic chained move,
    it would be automatically shipped according to DN1 shipment.
- a back order DN3 is automatically created with 30 PCE
    (from SUPPLIER to TRANSIT),
- chained move DN4 is automatically created with 30 PCE (from TRANSIT to INPUT)

Please note:
- In this case, workflow is closer to reality:
    all real stocks figures are correct and all relevant documents are created.
- Later on, DN2 and DN4 can be shipped separately
    (as they are setup as manual in this example)
- As many back order as necessary can be created:
    all chained moves are automatically updated and created accordingly
- this behavior works as well in case of sales orders.
""",
    'author': 'Elico Corp',
    'website': 'http://www.openerp.net.cn/',
    'depends': ['sale', 'stock', 'procurement', 'purchase'],
    "category": "Generic Modules/Inventory Control",
    'data': [
        'stock_view.xml'
    ],
    'test': ['test/test_back2back_order_proc.yml'],
    'installable': True,
    'active': False,
    'certificate': '',
}
