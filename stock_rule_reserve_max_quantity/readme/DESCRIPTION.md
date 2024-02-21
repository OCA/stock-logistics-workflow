This module extends the functionality of chained (pull) stock reservation to support the reservation of the total quantity brought by the done chained move lines. By default, the reservation on each step of the chain is limited to the need. If you pick more than the need, with this module the chained moves will reserve the total picked quantity.

This operation will only apply when the available quantity exceeds the demanded quantity and the stock rule linked to the stock move has the field *Reserve Max Quantity* activated.
