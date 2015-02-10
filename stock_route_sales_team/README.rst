Stock Route Sales Teams
=======================

Allow to configure a Route according to a sales team.

 * An option on the Routes define if the route can be used on sales
   teams or not
 * A new option on a sales team allows to choose the Route to use
   for their sales (the procurements will use this route, except if
   another one has been set on the lines)

Configuration
=============

The configurations available for this module are:

 * In `Warehouse > Configuration > Routes`, you can select the routes available
   for the sales teams
 * In `Sales > Sales Teams`, you can optionally choose a route that will be
   used for a team

Usage
=====

As soon as a sales order is created and its sales team has a route, the
stock will use this route.

Known issues / Roadmap
======================

Credits
=======

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
