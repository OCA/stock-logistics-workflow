.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=============================
The idea/ objective
=============================

Change the mechanism of reservation of products when the user confirms the quotation/ SO
and when the scheduler runs so products can be kept available in case
they are not needed immediately or to wait for a Purchase order to be received
(avoiding other delivery due to a partially booking that blocks the partially available order anyway).

Technical description for Definition of the reservation
=======================================================

Quotation/ SO adjustments:

 - In header:
    - Add field "Reservation Date" under Expected date of delivery (manual input)
 - Add tab "Related POs" with a new m2m field reservation_po_ids and display only 2 columns:
    - PO number
    - Reservation Date: a new field on PO, computed as latest date of related incoming shipments
Rename the status in stock move ("Waiting Another Move") and stock picking ("Waiting Another Operation")
with a suffix "or PO Reception or SO Reservation Date".

Expected Behavior
=================

If sale_order.reservation_date is set or sale_order.reservation_po_ids has some values:

 - The reservation of these products is not done when user confirms the SO
 - The reservation will be done by the scheduler
    - If the SO is linked to a PO, for each product listed in the SO:
      - The system will look for the product in on of the reservation_po_ids which is already received:
        - If it is found, the products (stock.quant) will be reserved
    - Otherwise, if the SO is not linked to a PO and has a reservation_date:
      - If the so.reservation_date is reached, then reserve the product
        Otherwise, we proceed as normal:
 - Reservation will take place when the user confirms the quotation/SO

Technical Solution to adjust the booking mechanism
==================================================

Override stock_move.action_assign:

pseudo-code:
```python
    if not move.so.reservation_date and len(move.so.reservation_po_ids) ==0:
        pass  #  continue the function action_assign
    elif move.product_id in \
              move.so.reservation_po_ids.last_picking_id.filtered(state=Done).\
              lines.product_id:
        pass  #  continue the function action_assign
    elif move.so.reservation_date < today():
        pass  #  continue the function action_assign
    else:
        return False
```
Notes
=====

 - Reservation Date on the SO has no impact if a product is part of one of the reservation_po_ids

Installation
============

No external library is used.

Configuration
=============

This module does not require any special configuration

Usage
=====
* Set date when you wanna reserve on Sale Order
* If Sale Order has Purchase order, link it into Related POs on Sale Order

Known issues / Roadmap
======================

* If Reservation Date is not set or Reservation Date is less than today, system will reserve as Odoo native
* If Reservation Date is greater to or equal to today, system will skip reservation

Credits
=======

Contributors
------------

* Jean-Charles Drubay <jc@komit-consulting.com>
* Cong, Duong Pham Thanh <cong.dpt@komit-consulting.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
