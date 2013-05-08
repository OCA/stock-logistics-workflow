# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2008 Raphaël Valyi
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name" : "Unique serial number management",
    "version" : "0.9.0",
    "author" : "Raphaël Valyi",
    "website" : "http://www.akretion.com",
    "depends" : ["product", "stock"],
    "category" : "Generic Modules/Inventory Control",
    "description":"""Turns production lot tracking numbers into unique per product instance code (serial number).
    Moreover, it
    1) adds a new checkbox on the product form to enable or disable this behavior (you should also enable in/out tracking)
    2) then forbids to perform a move if a move involves more than one product instance
    3) automagically splits up picking list movements into one movement per product instance
    4) turns incoming pickings into an editable grid where you can directly type the code
    of a new production number/code to create and associate to the move (it also checks it
    doesn't exist yet)
    
    Important Note 1: serial numbers are more easily encode using an editable tree grid, including a special field with new serial to be created.
    However, there is currently a limitation in the OpenObject framework preventing from easily changing non editable trees to editable trees
    by simple extension. Rather than overwriting all views, we prefer give only one example: the active customied view for easy serial encoding
    is available using Stock Management > Incoming Products. Looking  that that view definition, the same thing is easily achieved in
    other picking list, like out going products for instance. However it's not "on" by default, you would need to work it out for your case.
    Meanwhile, we hope Tiny add a third "merge_attributes" view extension point to the 3 existing ones: "before", "after" and "replace".
    It would basically simply merge the attributes given (redefined) in the original view XML and let inner content unchanged.
    Blueprint is registred here: https://blueprints.launchpad.net/openobject-server/+spec/merge-attributes-view-extension-point
    
    Important Note 2: this module doesn't split product bill of materials in MRP since they don't use pickings
    A good workaround when generating production orders manually one by one is too define several lines of individual products in nomemclatures
    and produce 1 by 1 (if possible) to make it easier to encode unique prodlot in production orders too.
    We would also like to extend this module to split automatic production orders (from MRP engine) into several individual production orders in order
    to make it easy to encode the serial numbers in the production. Let us know if you would like that simple extension to be made.
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["product_view.xml", "stock_view.xml"],
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: