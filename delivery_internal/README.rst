.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

=================
Delivery Internal
=================

This module adds the concept of an internal delivery carrier to `delivery
.carrier`. When the `delivery_type` of a carrier is set to `Internal`, any
pickings shipped from that carrier will create `Requests For Pickup`. These
requests for pickup will in-turn create two pickings, one for the carrier to
pick up and one for the buyer to receive.

The Requests for pickup can also be configured to allow for Cash On
Delivery. Choosing this method will create two more pickings for the cash
pickup and subsequent delivery.



Usage
=====

To use, simply add a Delivery Carrier with the Type set to Internal.

Known issues / Roadmap
======================

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-workflow/issues>`_. In case of
trouble, please check there if your issue has already been reported. If you
spotted it first, help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Ted Salmon <tsalmon@laslabs.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
