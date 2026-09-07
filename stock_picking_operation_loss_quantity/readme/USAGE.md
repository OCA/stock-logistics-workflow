- You need to have enabled the 'Show Detailed Operations' on the Picking type(s) you
  want.
- Go to Inventory > Operations > Transfers
- Choose the one you want to manage.
- In the 'Detailed Operations' tab, fill in the done quantities as usual.
- If for one line, you don't find physically the whole product quantity, you'll be able
  to declare the loss for the difference between the reserved one and the done one.
- To do so, fill in the found quantity in the Done column, then click on the 'Loss'
  button.
- The reserved quantity of that line is reduced to the done quantity, and a stock move
  of the 'Loss' picking type is created and reserves whatever remains available on that
  same quant (product, location, lot, package, owner). This locks it: no other
  operation can reserve it while the loss is being investigated.
- Odoo then tries to find the missing quantity elsewhere in stock so the picking can
  still be completed. If other stock is found (another location or lot), it is reserved
  on a new operation line - the line the operator already processed is never modified.
  If nothing else is available, the line is simply left with nothing reserved.
- An operator can then check the pickings of the 'Loss' picking type and either
  validate them (confirming the loss) or cancel them (releasing the locked quantity
  back to stock). Applying an inventory adjustment on a locked quant also releases it
  automatically.