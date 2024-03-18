This module is currently used as a base for shipment reporting per picking type (aka zone).

e.g. :

A shipment report that contains several products coming from differents picking
zones (parts of stock).

.. code-block:: shell


                                STOCK

        FOOD                    DRUGS                   HARDWARE

        ||                        ||                       ||
        ||                        ||                       ||
        \/                        \/                       \/
  Picking Type Food       Picking Type Drugs        Picking Type HARDWARE
        ||                        ||                       ||
        ||                        ||                       ||
        \/                        \/                       \/

                                Pack

                                  ||
                                  ||
                                  \/

                                Ship => X products from Food
                                        Y products from Drugs
                                        Z products from Hardware
