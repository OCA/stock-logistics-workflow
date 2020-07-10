The module contains the development that allows creating the expeditions section for later use.

In Inventory> Operations the "Expeditions" menu section is added

## Crons

## Shipping Expedition Update State
Frequency: 1 time every hour

Description:
Regarding all shipments that are not in states: delivered or canceled, their states are updated so that the addons of each type of transport (shipping_expedition_nacex, shipping_expedition_cbl, shipping_expedition_txt) include the function to update the corresponding expedition.
