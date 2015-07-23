# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

stock_inventory_id = int(terminal.tmp_val1)
stock_inventory_obj = pool.get('stock.inventory')
stock_inventory_obj.action_confirm(cr, uid, [stock_inventory_id], context=context)
stock_inventory_obj.action_done(cr, uid, [stock_inventory_id], context=context)

act = 'F'
res = [
    'Inventory done !',
]
