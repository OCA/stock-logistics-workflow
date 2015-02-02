Stock Ownership By Move
=======================

This module lets you use the ownership in each move of a picking when receiving
shipments. All other stock functionalities already use the owner in the move,
and not the one in the picking.

Configuration
=============

Installing this module, the setting to show owners will be enabled
automatically.

Usage
=====

- In a picking, you can set the owner on every line.
- When transferring a picking, lines with different owners will not be grouped.
- In the transfer details wizard, the owner of every line can be changed.
- After the transfer, the owner is also shown in the Operations tab.
- Generated quants have the selected owner.
- The "Owner" field is not shown anymore in the picking.

Known Issues / Roadmap
======================

- Show the owner also in the form and tree views of the move when not inside
  a picking.
- The "Owner" field in the move form view inside the picking is already added
  in the module stock_ownership_availability_rules. It could be added here
  instead.
- Check what happens when using the barcode interface.
- The original method tries to respect the order of moves when generating pack
  operations. We don't, because we use a dictionary which is unordered.

Credits
=======

Contributors
------------

* Leonardo Pistone <leonardo.pistone@camptocamp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
