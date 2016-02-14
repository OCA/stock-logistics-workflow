.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Split picking
-------------

This module adds a "Split" button on the outgoing pickings form.

It works like the classical picking Transfer but it leaves both
pickings (picking and its backorder) as confirmed without
processing the transfer.

Installation
============

This module only needs `stock` module.

Known issues / Roadmap
======================

* When splitting a picking in an unassigned state, wizard won't
  be auto completed with picking lines.

Credits
=======

Contributors
------------

* Nicolas Bessi <nicolas.bessi@camptocamp.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
