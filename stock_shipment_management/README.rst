Shipment plan management
========================

This module allows you to manage your transport.

A shipment plan represent a kind of "contract" with your carrier.
It will show you show you transit status of your deliveries or reception.

Configuration
=============

To configure this module, you need to configure your Warehouse to use Transit Location

 * Go to *Warehouse/Configuration/Warehouse*
 * Edit your warehouse as follow:

   * **Incoming Shipments**: *Receive goods directly in stock from Transit (transit + 1 step)*

     and / or

   * **Outgoing Shippings**: *Ship from stock to Transit location*

Usage
=====

To create shipment plan, you need to:

 * Go to Picking list in *Warehouse/Operations/All Operations*

   or

 * Go to Move list in *Warehouse/Traceability/Stock Moves*

 * Select or Open some pickings/moves
 * Use **Add to a shipment** wizard

There, you will be able to create a new shipment or add
selected moves to an existing shipment.

Only moves from same source and destination with same carrier can be bound together.


Known issues / Roadmap
======================

TODO:

 * Partial shipment: creation of a new shipment with shipped residual.
 * Manage lost in transit product

Credits
=======

Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

