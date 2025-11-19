This module was developed because sometimes we don't want our stock movements to be merged if goes to different moves because:
- Sale free products that must be invoiced separatelly (for example, get 2 + 1 free)
- Use warehouse with 2 or 3 steps in Outgoing Shipments
- Use products with Invoicing Policy: Delivered Quantities

All of these conditions must be met for this module to be really useful.

## Use case example:

We have an order with two lines of the same product that need to be weighed (kg) and the offer is "get 2 + 1 free".

Each piece of Fish measures aproximately 1kg and we assume you know how many Fishes you need to take.

The lines of the sale would be like this:
- 2 pieces of Fish for aproximately 2kg in total.
- 1 piece of Fish for aproximately 1kg in total with 100% discount.

## Odoo Core VS. Module: Workflow comparison

| **Odoo Core** | **With this module** |
|---|---|
| The OUT step will not be grouped, so we will have 2 moves. | The OUT step will not be grouped, so we will have 2 moves. |
| | |
| The PICK step will be grouped into one line, telling you that 3 kgs must be demanded | Since we have 2 separate moves on the OUT step, we don't want to merge moves in the PICK step. PICK step will tell you that 3kgs must be demanded into 2 separate moves. |
| | |
| When you measure the 3 fishes in the PICK step, we get 1.9kg for the 2 Fishes and 0.7kg for the free Fish. 2.6kg in total. | When you measure the 3 fishes in the PICK step, we get 1.9kg for the 2 Fishes and 0.7kg for the free Fish. 2.6kg in total. |
| | |
| Confirm the PICK step. When you reserve quantities on OUTGOING step, 2kg will go to the 2 Fishes and 0.6kg to the free Fish. | Confirm the PICK step. When you reserve quantities on OUTGOING step, 1.9kg will go to the 2 Fishes and 0.7kg to the free Fish. |
| | |
| Your invoice to the customer will be 2kg for the 2 pieces and 0.6kg for the free fish. | Your invoice to the customer will be 1.9kg for the 2 pieces and 0.7kg for the free fish. |
| | |
| This is not correct: The 2 pices of Fish should be invoiced for 1.9kg and the free fish should be invoiced for 0.7kg at 100% discount. | This is correct |


If you also don't want to have to reweigh in the last step if you exceeded the quantity demanded (Fishes weight 1.14kg each for example), you might be interested in this module:
  - stock_rule_reserve_max_quantity
